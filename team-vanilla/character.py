import json

class Character:

    def __init__(self, player_id, hp=100, attack=10, speed=10, defence=10):
        self.player_id = player_id
        self.stats = dict()
        self.stats["hp"] = hp
        self.stats["attack"] = attack
        self.stats["speed"] = speed
        self.stats["defence"] = defence

    def json_stats(self):
        return self.stats
