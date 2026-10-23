"""Книга приёмов. Патч 1.8.

Контракт приёма:  move(user, /, *targets, crit=False, **effects) -> (урон, статусы) | None
Движок зовёт:     cast(book, name, user, *targets, log=..., **effects)

Автопроверка импортирует этот модуль и ждёт в нём learn, cast, make_strike,
limited и book_for — см. README, раздел «Как сдавать».
"""
import inspect

# Эталонная сигнатура контракта. По ней сравниваем *виды* параметров.
def _contract(user, /, *targets, crit=False, **effects):
    pass

_CONTRACT_KINDS = tuple(
    p.kind for p in inspect.signature(_contract).parameters.values()
)

# Стоимость маны у приёмов, которым она нужна.
_NOVA_MANA = 10
_HEAL_AMOUNT = 20
_STRIKE_DAMAGE = 10
_CRIT_DAMAGE = 30
_CRIT_DAMAGE_NORMAL = 15


def learn(book, move):
    """Положить приём в книгу, если его сигнатура совпадает с контрактом. Иначе TypeError."""
    try:
        kinds = tuple(
            p.kind for p in inspect.signature(move).parameters.values()
        )
    except (TypeError, ValueError) as exc:
        raise TypeError("move has no inspectable signature") from exc
    if kinds != _CONTRACT_KINDS:
        raise TypeError(
            f"incompatible signature: {kinds}, expected {_CONTRACT_KINDS}"
        )
    book[move.__name__] = move
    return move


def strike(user, /, *targets, crit=False, **effects):
    """Удар по одной цели: 10 урона. Без целей — 0 урона, но выполняется."""
    if not targets:
        return (0, {})
    dmg = _STRIKE_DAMAGE
    targets[0]["hp"] -= dmg
    return (dmg, {})


def nova(user, /, *targets, crit=False, **effects):
    """Удар по площади: 5 урона каждой цели, стоит 10 маны."""
    if user["mana"] < _NOVA_MANA:
        return None
    user["mana"] -= _NOVA_MANA
    dmg = 5 * len(targets)
    for t in targets:
        t["hp"] -= 5
    return (dmg, {})


def heal(user, /, *targets, crit=False, **effects):
    """Лечение себя: цели игнорируются, крит не действует."""
    user["hp"] += _HEAL_AMOUNT
    return (0, {})


def status(user, /, *targets, crit=False, **effects):
    """Накладывает **effects на цели. Статус поверх такого же — заменяет."""
    applied = {}
    for t in targets:
        t["effects"].update(effects)
        applied.update(effects)
    return (0, applied)


def critical_strike(user, /, *targets, crit=False, **effects):
    """Удар по одной цели; crit=True — сильнее. Крит только по имени."""
    if not targets:
        return (0, {})
    dmg = _CRIT_DAMAGE if crit else _CRIT_DAMAGE_NORMAL
    targets[0]["hp"] -= dmg
    return (dmg, {})


def make_strike(power, element):
    """Фабрика стихийных ударов: приём силы power со стихией element."""
    def elemental_strike(user, /, *targets, crit=False, **effects):
        if not targets:
            return (0, {})
        dmg = power * 2 if crit else power
        targets[0]["hp"] -= dmg
        return (dmg, {})
    elemental_strike.__name__ = f"{element}{power}"
    elemental_strike.__qualname__ = f"{element}{power}"
    return elemental_strike


def limited(move, charges):
    """Обёртка с зарядами: считает их через nonlocal, при нуле возвращает None.

    Заряды принадлежат *экземпляру обёртки*, поэтому book_for создаёт свой
    limited для каждого персонажа.
    """
    remaining = charges

    def charged(user, /, *targets, crit=False, **effects):
        nonlocal remaining
        if remaining <= 0:
            return None
        result = move(user, *targets, crit=crit, **effects)
        if result is None:           # не хватило маны — заряд не тратим
            return None
        remaining -= 1
        return result

    charged.__name__ = move.__name__
    charged.__qualname__ = move.__qualname__
    return charged


def book_for(character):
    """Книга: strike, nova, heal, status, critical_strike и огни fire10/20/40.

    Комплект зарядов nova — свой у каждого персонажа (свой limited).
    """
    book = {}
    learn(book, strike)
    learn(book, limited(nova, 3))     # свежие 3 заряда на этого персонажа
    learn(book, heal)
    learn(book, status)
    learn(book, critical_strike)
    for power in (10, 20, 40):
        learn(book, make_strike(power, "fire"))
    return book


def cast(book, name, user, /, *targets, log, **effects):
    """Движок: найти приём, разложить аргументы по его сигнатуре, записать в журнал."""
    move = book[name]

    # Логический аргумент на месте цели — ошибка, а не «крит уехал в цель».
    if any(isinstance(t, bool) for t in targets):
        raise TypeError("bool passed positionally as target; crit is keyword-only")

    sig = inspect.signature(move)
    bound = sig.bind(user, *targets, **effects)
    bound.apply_defaults()

    result = move(*bound.args, **bound.kwargs)
    if result is None:
        return None

    damage, _applied = result
    log.append((user["name"], name, damage))
    return result


def book_for(character):
    """Книга: strike, nova, heal, status, critical_strike и огни fire10/20/40.

    Комплект зарядов nova — свой у каждого персонажа.
    """
    raise NotImplementedError
