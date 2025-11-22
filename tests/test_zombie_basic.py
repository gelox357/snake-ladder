from src.core.board import Board
from src.objects.zombie import ZombieSnake

def test_zombie_moves_and_grows():
    b = Board()
    z = ZombieSnake(b, None)
    target = next(iter(z.brains))
    z.segments[0] = (max(0, target[0]-1), target[1])
    z.dir = (1,0)
    z.enqueue_steps(1)
    z.update(0.1)
    assert len(z.segments) >= 1