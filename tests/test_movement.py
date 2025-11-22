from src.core.player import Player

def test_overshoot_bounce():
    p = Player("A", (0,0,0), None)
    p.square = 97
    p.enqueue_steps(6)
    for _ in range(6):
        p.step()
    assert p.square == 99