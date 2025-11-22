from src.objects.dice import Dice
from src.services.assets import AssetLoader

def test_dice_roll_finishes():
    d = Dice(AssetLoader({"images":{},"sounds":{}}))
    d.start()
    t = 0
    while not d.update(0.1):
        t += 0.1
    assert 1 <= d.face <= 6