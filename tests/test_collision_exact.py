from src.core.game import Game
from src.scenes.board_scene import BoardScene

def test_ladder_applies_on_exact_landing():
    g = Game()
    scene = BoardScene(g, ["A","B"], True, "Classic")
    # Move to 63 (ladder base) then apply collision
    p = scene.players[0]
    p.square = 62
    p.enqueue_steps(1)
    # Advance update until step consumed
    for _ in range(2):
        scene.update(0.2)
    assert p.square == 81

def test_snake_applies_on_exact_landing():
    g = Game()
    scene = BoardScene(g, ["A","B"], True, "Classic")
    p = scene.players[0]
    p.square = 97
    p.enqueue_steps(1)  # land on 98 (snake head)
    for _ in range(2):
        scene.update(0.2)
    assert p.square == 79