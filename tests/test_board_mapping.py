from src.core.board import Board

def test_board_numbering_positions():
    b = Board()
    assert b.square_pos(1) != b.square_pos(2)
    assert b.square_pos(10)[0] > b.square_pos(9)[0]
    assert b.square_pos(11)[0] > b.square_pos(12)[0]

def test_collision_maps():
    b = Board()
    s, k = b.apply_collision(98)
    assert s == 79
    s, k = b.apply_collision(28)
    assert s == 84