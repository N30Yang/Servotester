from servotester.main import draw_bar

def test_bar_logic():
    result = draw_bar(0)
    assert "[--------------------]" in result
    result = draw_bar(4095)
    assert "[████████████████████]" in result