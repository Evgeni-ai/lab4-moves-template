"""Книга приёмов. Патч 1.8.

Контракт приёма:  move(user, /, *targets, crit=False, **effects) -> (урон, статусы) | None
Движок зовёт:     cast(book, name, user, *targets, log=..., **effects)

Автопроверка импортирует этот модуль и ждёт в нём learn, cast, make_strike,
limited и book_for — см. README, раздел «Как сдавать».
"""
import inspect
from inspect import Parameter


# Проверка на сигнатуру
import inspect


def aaaa(user, /, *targets, crit=False, **effects):
    raise NotImplementedError


def same_types(f, g):
    # Сравниваем ВИДЫ параметров и значения по умолчанию, а не аннотации:
    # по контракту сигнатура совпадает «по видам, а не по именам».
    return (
        [(p.kind, p.default) for p in inspect.signature(f).parameters.values()]
        ==
        [(p.kind, p.default) for p in inspect.signature(g).parameters.values()]
    )


def learn(book, move):
    """Положить приём в книгу, если его сигнатура совпадает с контрактом. Иначе TypeError."""
    if same_types(move, aaaa):
        book[move.__name__] = move
    else:
        raise TypeError("приём не корректен")


def hit(targets, dmg):
    for t in targets:
        if not isinstance(t, dict):
            raise TypeError("target must be a character dict")
        t["hp"] = max(t["hp"] - dmg, 0)
    return dmg * len(targets)


def eff(targets, **ef):
    for t in targets:
        if not isinstance(t, dict):
            raise TypeError("target must be a character dict")
        t.setdefault("effects", {})
        for key in ef:
            t["effects"][key] = ef[key]


def strike(user, /, *targets, crit=False, **effects):
    for t in targets:
        if not isinstance(t, dict):
            raise TypeError("target must be a character dict")
    if user["mana"] < 5:
        return None
    if len(targets) != 1:
        return None
    user["mana"] -= 5
    dmg = hit(targets, 10)
    return dmg, {}


def critical_strike(user, /, *targets, crit=False, **effects):
    for t in targets:
        if not isinstance(t, dict):
            raise TypeError("target must be a character dict")
    if user["mana"] < 7:
        return None
    if len(targets) != 1:
        return None
    user["mana"] -= 7
    dmg = hit(targets, 20 if crit else 10)
    return dmg, {}


def nova(user, /, *targets, crit=False, **effects):
    for t in targets:
        if not isinstance(t, dict):
            raise TypeError("target must be a character dict")
    if user["mana"] < 10:
        return None
    user["mana"] -= 10
    dmg = hit(targets, 14 if crit else 7)   # 0, если целей нет
    return dmg, {}


def heal(user, /, *targets, crit=False, **effects):
    # цели игнорируются — лечим только себя
    if user["mana"] < 5:
        return None
    user["mana"] -= 5
    user["hp"] = user.get("hp", 0) + 20
    return 0, {}


def status(user, /, *targets, crit=False, **effects):
    for t in targets:
        if not isinstance(t, dict):
            raise TypeError("target must be a character dict")
    if user["mana"] < 10:
        return None
    user["mana"] -= 10
    eff(targets, **effects)
    return 0, dict(effects)


def cast(book, name, user, /, *targets, log=None, **effects):
    """Движок: найти приём по имени, разложить аргументы по его сигнатуре, записать в журнал."""
    if name not in book:
        return None
    fn = book[name]
    sig = inspect.signature(fn)
    bound = sig.bind(user, *targets, **effects)
    result = fn(*bound.args, **bound.kwargs)
    if result is not None and log is not None:
        player = user.get("name", user)       
        log.append((player, name, result[0]))
    return result


def make_strike(power, element):
    """Фабрика стихийных ударов: возвращает приём силы power со стихией element."""
    def move(user, /, *targets, crit=False, **effects):
        for t in targets:
            if not isinstance(t, dict):
                raise TypeError("target must be a character dict")
        if user["mana"] < 5:
            return None
        user["mana"] -= 5
        dmg = hit(targets, power)
        return dmg, {}

    move.__name__ = f"{element}{power}"     # fire10 / fire20 / fire40
    return move


def limited(move, charges):
    """Обёртка с зарядами: считает их через nonlocal, при нуле возвращает None."""
    counters = {}   # id(user) -> [user_ref, remaining]; per-character

    def wrapper(user, /, *targets, crit=False, **effects):
        nonlocal counters
        key = id(user)
        entry = counters.get(key)
        if entry is None or entry[0] is not user:
            entry = [user, charges]
            counters[key] = entry
        if entry[1] <= 0:
            return None
        result = move(user, *targets, crit=crit, **effects)
        if result is not None:
            entry[1] -= 1
        return result

    wrapper.__name__ = move.__name__
    wrapper.__signature__ = inspect.signature(move)
    return wrapper


def book_for(character):
    """Книга: strike, nova (3 заряда), heal, status, critical_strike, fire10/20/40."""
    book = {}
    learn(book, strike)
    learn(book, limited(nova, 3))
    learn(book, heal)
    learn(book, status)
    learn(book, critical_strike)
    for power in (10, 20, 40):
        learn(book, make_strike(power, "fire"))
    return book
