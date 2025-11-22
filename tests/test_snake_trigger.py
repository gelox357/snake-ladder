from src.scenes.board_scene import BoardScene
from src.core.game import Game

def test_snake_eat_trigger():
    g = Game()
    scene = BoardScene(g, ["A","B"], True, "Classic")
    scene.players[0].square = 98
    new, kind = scene.board.apply_collision(98)
    assert kind == "snake"
    for s in scene.snakes:
        if s.head_square == 98:
            s.trigger_eat()
            assert s.eat_time > 0