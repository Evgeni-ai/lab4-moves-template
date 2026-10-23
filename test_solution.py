"""Ваши тесты. Реализацию берите из фикстуры impl, персонажей — из chars (см. conftest.py):

    python3 -m pytest -q                          # на вашем solution.py — должно быть зелёным
    python3 -m pytest -q --impl valera_adapter    # на коде Валеры — должно быть красным

Что нужно проверить — в README; количество тестов не фиксировано.
"""


def test_three_fires_hit_differently(impl, chars):
    sonya, marat = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    dmg = [impl.cast(book, name, sonya, marat, log=[])[0] for name in ("fire10", "fire20", "fire40")]
    assert dmg == [10, 20, 40]

import pytest


# 1. три огня бьют на 10, 20 и 40
def test_three_fires(impl, chars):
    sonya, foe = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    for power in (10, 20, 40):
        foe["hp"] = 100
        log = []
        res = impl.cast(book, f"fire{power}", sonya, foe, log=log)
        assert res is not None
        assert res[0] == power, f"fire{power} нанёс {res[0]}, ожидали {power}"
        assert log == [("Соня", f"fire{power}", power)]


# 2. заряды Сони и Лины независимы
def test_charges_independent(impl, chars):
    sonya, lina, foe = chars("Соня", "Лина", "Марат")
    sb, lb = impl.book_for(sonya), impl.book_for(lina)

    for _ in range(3):
        assert impl.cast(sb, "nova", sonya, foe, log=[]) is not None
    assert impl.cast(sb, "nova", sonya, foe, log=[]) is None

    # у Лины свой комплект: три заряда ещё на месте
    for _ in range(3):
        assert impl.cast(lb, "nova", lina, foe, log=[]) is not None
    assert impl.cast(lb, "nova", lina, foe, log=[]) is None


# 3. два боя подряд — два разных журнала
def test_two_battles_logs(impl, chars):
    sonya, foe = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    log1, log2 = [], []
    impl.cast(book, "strike", sonya, foe, log=log1)
    impl.cast(book, "strike", sonya, foe, log=log2)
    assert len(log1) == 1 and len(log2) == 1
    assert log1 is not log2
    assert log1[0][1] == "strike" and log2[0][1] == "strike"


# 4. learn отвергает приём с неправильной сигнатурой
def test_learn_rejects_bad_signature(impl):
    book = {}

    def bad(a, b):              # нет /, *targets, crit, **effects
        return (0, {})

    with pytest.raises(TypeError):
        impl.learn(book, bad)


# 5. cast(book, "strike", user, foe, True) — TypeError, крит не уезжает в цели
def test_bool_target_raises(impl, chars):
    sonya, foe = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    with pytest.raises(TypeError):
        impl.cast(book, "strike", sonya, foe, True, log=[])


# 6. critical_strike с crit=True бьёт сильнее, чем без крита
def test_crit_stronger(impl, chars):
    sonya, foe = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    foe["hp"] = 100
    d1 = impl.cast(book, "critical_strike", sonya, foe, log=[])[0]
    foe["hp"] = 100
    d2 = impl.cast(book, "critical_strike", sonya, foe, log=[], crit=True)[0]
    assert d2 > d1


# 7. приём без маны возвращает None, цель не задета
def test_no_mana_returns_none(impl, chars):
    sonya, foe = chars("Соня", "Марат")
    sonya["mana"] = 0
    book = impl.book_for(sonya)
    hp_before = foe["hp"]
    assert impl.cast(book, "nova", sonya, foe, log=[]) is None
    assert foe["hp"] == hp_before


# 8. результат status — кортеж, статус из **effects оказался на цели
def test_status_applied(impl, chars):
    sonya, foe = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    res = impl.cast(book, "status", sonya, foe, log=[], poison=1)
    assert isinstance(res, tuple)
    assert foe["effects"].get("poison") == 1


# 9. тест, который падает на коде Валеры и проходит на решении
def test_fails_on_valera(impl, chars):
    # (a) heal есть в книге и реально лечит
    sonya, foe = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    assert "heal" in book
    sonya["hp"] = 50
    impl.cast(book, "heal", sonya, log=[])
    assert sonya["hp"] > 50

    # (b) у Лины своя книга с полным комплектом зарядов
    sonya, lina, foe = chars("Соня", "Лина", "Марат")
    sb, lb = impl.book_for(sonya), impl.book_for(lina)
    for _ in range(3):
        impl.cast(sb, "nova", sonya, foe, log=[])
    assert impl.cast(lb, "nova", lina, foe, log=[]) is not None

    # (c) в приёмах нет изменяемых значений по умолчанию
    for name, move in book.items():
        for d in (getattr(move, "__defaults__", None) or ()):
            assert not isinstance(d, (list, dict, set)), f"{name}: mutable default"
        for d in (getattr(move, "__kwdefaults__", None) or {}).values():
            assert not isinstance(d, (list, dict, set)), f"{name}: mutable kwdefault"
