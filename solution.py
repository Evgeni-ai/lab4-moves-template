"""Книга приёмов. Патч 1.8.

Контракт приёма:  move(user, /, *targets, crit=False, **effects) -> (урон, статусы) | None
Движок зовёт:     cast(book, name, user, *targets, log=..., **effects)

Автопроверка импортирует этот модуль и ждёт в нём learn, cast, make_strike,
limited и book_for — см. README, раздел «Как сдавать».
"""
import inspect


def learn(book, move):
    """Положить приём в книгу, если его сигнатура совпадает с контрактом. Иначе TypeError."""
    raise NotImplementedError


def cast(book, name, user, /, *targets, log, **effects):
    """Движок: найти приём по имени, разложить аргументы по его сигнатуре, записать в журнал."""
    raise NotImplementedError


def make_strike(power, element):
    """Фабрика стихийных ударов: возвращает приём силы power со стихией element."""
    raise NotImplementedError


def limited(move, charges):
    """Обёртка с зарядами: считает их через nonlocal, при нуле возвращает None."""
    raise NotImplementedError


def book_for(character):
    """Книга: strike, nova, heal, status, critical_strike и огни fire10/20/40.

    Комплект зарядов nova — свой у каждого персонажа.
    """
    raise NotImplementedError



