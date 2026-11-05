"""Ваши тесты. Реализацию берите из фикстуры impl, персонажей — из chars (см. conftest.py):

    python3 -m pytest -q                          # на вашем solution.py — должно быть зелёным
    python3 -m pytest -q --impl valera_adapter    # на коде Валеры — должно быть красным

Что нужно проверить — в README; количество тестов не фиксировано.
"""
import pytest

def test_three_fires_hit_differently(impl, chars):
    sonya, marat = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    dmg = [impl.cast(book, name, sonya, marat, log=[])[0] for name in ("fire10", "fire20", "fire40")]
    assert dmg == [10, 20, 40]

def test_independent_charges(impl, chars):
    sonya, marat, lina = chars("Соня", "Марат", "Лина")
    sonya_book = impl.book_for(sonya)
    lina_book = impl.book_for(lina)
    sonya_nova = sonya_book["nova"]
    lina_nova = lina_book["nova"]    
    impl.cast(lina_book, "nova", lina, marat, log=[])
    assert sonya_nova.remaining(sonya) != lina_nova.remaining(lina)

def test_two_fight_in_a_row(impl, chars):
    sonya, marat, lina = chars("Соня", "Марат", "Лина")

    book1 = impl.book_for(sonya)                 # бой 1
    log1 = []
    impl.cast(book1, "strike", sonya, marat, log=log1)

    book2 = impl.book_for(sonya)                 # бой 2 — новая книга
    log2 = []
    impl.cast(book2, "strike", marat, lina, log=log2)

    assert log1 is not log2                      # разные объекты
    assert len(log1) == 1                        # в каждом — только свой
    assert len(log2) == 1
    assert log1[0][0] == "Соня"                  # в log1 — Соня
    assert log2[0][0] == "Марат"  

def test_uncoorect_signatyre(impl):
    def bad_move(a,b):
        return a+b
    with pytest.raises(TypeError):
        impl.learn({}, bad_move)

def test_no_position_crit(impl, chars):
    sonya, lina = chars("Соня", "Лина")
    lina_book = impl.book_for(lina)
    with pytest.raises(TypeError):
        impl.cast(lina_book, "strike", lina, sonya, True, log=[])

def test_crit(impl,chars):
    sonya, lina = chars("Соня", "Лина")
    lina_book = impl.book_for(lina)
    dmg1 = impl.cast(lina_book, "critical_strike", lina, sonya, crit = False, log=[])[0]
    dmg2 = impl.cast(lina_book, "critical_strike", lina, sonya, crit = True, log=[])[0]
    assert dmg2 > dmg1

def test_no_mana(impl, chars):
    sonya, lina = chars("Соня", "Лина")
    lina_book = impl.book_for(lina)
    sonya["hp"] = 100
    lina["mana"] = 0
    result = impl.cast(lina_book, "critical_strike", lina, sonya, crit = False, log=[])
    assert result == None
    assert sonya["hp"] == 100

def test_effects(impl,chars):
    sonya, lina = chars("Соня", "Лина")
    lina_book = impl.book_for(lina)
    result = impl.cast(lina_book, "critical_strike", lina, sonya, log=[], Ponos=1)[1]
    assert type(result) == dict
    assert result == sonya["effects"]
     
def test_valera(impl,chars):
    sonya, marat = chars("Соня", "Марат")
    book = impl.book_for(sonya)
    dmg = [impl.cast(book, name, sonya, marat, log=[])[0] for name in ("fire10", "fire20", "fire40")]
    assert dmg == [10, 20, 40]

    
