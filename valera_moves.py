"""Способности, патч 1.8. Валера.

Приём — функция, движок зовёт её по имени из книги. Журнал боя ведётся сам,
заряды считаются сами, огненные приёмы трёх сил сделал одной строкой.
Запускается, тесты не писал.
"""

import inspect

def hit(targets, dmg):
    for t in targets:
        t["hp"] = max(t["hp"]-dmg , 0)
    return dmg * len(targets)


def strike(user, target, crit=False, log=[]):
    """Удар: 10 урона, при крите вдвое. Журнал можно не передавать — заведётся сам."""

    if user["mana"] < 5:
        return None
    if len(target) != 1:
        return None
    
    user["mana"] -= 5
    dmg = hit([target], 20 if crit else 10)
    log.append((user["name"], "strike", dmg))
    return dmg, {}


def nova(user, *targets, crit=False, charges={"left": 3}, log=[]):
    """Взрыв: 30 урона по площади, при крите вдвое, три заряда на бой."""
    if charges["left"] == 0:
        return None
    charges["left"] -= 1
    dmg = hit(targets, 60 if crit else 30)
    log.append((user["name"], "nova", dmg))
    return dmg, {"burn": True}


fires = [lambda user, *targets: (hit(targets, power), {"burn": True}) for power in (10, 20, 40)]
BOOK = {"strike": strike, "nova": nova, "fire1": fires[0], "fire2": fires[1], "fire3": fires[2]}


def cast(name, user, *targets, **effects):
    return BOOK[name](user, *targets, **effects)


print(inspect.signature(nova))