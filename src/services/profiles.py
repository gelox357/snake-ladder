import os
import json

class Profile:
    def __init__(self, name):
        self.name = name
        self.color = (66,135,245)
        self.avatar = None
        self.games_played = 0
        self.wins = 0
        self.items_collected = 0
        self.high_score = 0
        self.levels_completed = 0
        self.achievements = []

    def to_dict(self):
        return {
            "name": self.name,
            "color": self.color,
            "avatar": self.avatar,
            "games_played": self.games_played,
            "wins": self.wins,
            "items_collected": self.items_collected,
            "high_score": self.high_score,
            "levels_completed": self.levels_completed,
            "achievements": self.achievements,
        }

    @staticmethod
    def from_dict(d):
        p = Profile(d.get("name","Player"))
        p.color = tuple(d.get("color", (66,135,245)))
        p.avatar = d.get("avatar")
        p.games_played = d.get("games_played",0)
        p.wins = d.get("wins",0)
        p.items_collected = d.get("items_collected",0)
        p.high_score = d.get("high_score",0)
        p.levels_completed = d.get("levels_completed",0)
        p.achievements = d.get("achievements",[])
        return p

class ProfileStore:
    def __init__(self, path="profiles.json"):
        self.path = path
        self.data = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.data = {k: Profile.from_dict(v) for k,v in raw.items()}
        else:
            self.data = {}

    def save(self):
        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump({k:v.to_dict() for k,v in self.data.items()}, f, indent=2)

    def get(self, name):
        if name not in self.data:
            self.data[name] = Profile(name)
        return self.data[name]

    def update_win(self, name, score):
        p = self.get(name)
        p.games_played += 1
        p.wins += 1
        p.high_score = max(p.high_score, score)
        if "First Win" not in p.achievements:
            p.achievements.append("First Win")
        self.save()

    def update_play(self, name):
        p = self.get(name)
        p.games_played += 1
        self.save()