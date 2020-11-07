import json
import typing
import attr


@attr.s(auto_attribs=True)
class Move(object):
    stats: typing.Dict
    description: str
    power: int
    # todo add stuff like accuracy


@attr.s(auto_attribs=True, frozen=True)  # this means that modification need to replace the entire object
class Character:
    player_id: int
    stats: typing.Dict[str, int]

    @classmethod
    def from_id(cls, player_id, hp=100, attack=10, speed=10, defence=10):
        return cls(player_id, {'hp': hp, 'attack': attack, 'speed': speed, 'defence': defence})

    def json_stats(self):
        return self.stats


class BattleUpdate(object):
    def __init__(self):
        pass


@attr.s(auto_attribs=True)
class BattleMoveMade(BattleUpdate):
    move: Move
    health_remaining: int
    defender: Character


class BattleFinished(BattleUpdate):
    def __init__(self):
        super().__init__()


@attr.s(auto_attribs=True)
class Battle(object):
    participants: typing.Dict[Character, typing.Dict]
    moves: typing.List[Move] = []

    @classmethod
    def from_participants(cls, characters: typing.List[Character]):
        return cls({character: character.stats.copy() for character in characters}, [])

    def move(self, attacking_character, move: Move):
        """
        One of the participants makes a move
        :param move:
        :param attacker:
        :return:
        """
        assert len(self.participants) == 2, 'need to have only 2 players battling'
        # some logic to get the defender correctly
        attacker, defender = self.participants
        if attacking_character == defender:
            defender = attacker
            attacker = attacking_character

        # todo we could have some advanced calculation of how much damage and stuff goes here

        self.participants[defender]['hp'] -= move.power
        self.moves.append(move)
        if self.participants[defender]['hp'] <= 0:
            # the battle is over as the defender's HP got below 0
            return BattleFinished(victor=attacker)
        # the battle continues
        return BattleMoveMade(move, self.participants[defender]['hp'], defender)
