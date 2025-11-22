from src.objects.dice import Dice
from src.services.assets import AssetLoader

def test_uniform_faces():
    d = Dice(AssetLoader({"images":{},"sounds":{}}))
    counts = [0]*6
    for _ in range(600):
        d.start()
        t = 0
        while not d.update(0.05):
            t += 0.05
        counts[d.face-1] += 1
    for c in counts:
        assert c > 60