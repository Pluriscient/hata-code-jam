from hata import Client, Message, Embed
import json
from hata.ext.commands import setup_ext_commands
from character import *
from hata import KOKORO, Lock, enter_executor

import cattr

FILE_LOCK = Lock(KOKORO)

secrets = json.load(open('secrets.json'))
Faito = Client(secrets['token'])
setup_ext_commands(Faito, '!')
# dictionary pointing user.id -> character
characters = {}
# list of battles
battles = []
battle_locks = []
characters_lock = Lock(KOKORO)


@Faito.events
async def ready(client):
    print(f'{client:f} logged in.')


@Faito.commands
async def ping(client, message):
    await client.message_create(message.channel, 'pong')


@Faito.commands
async def signup(client, message):
    global characters
    if message.author.is_bot:
        return

    async with characters_lock:
        if message.author.id in characters:
            await client.message_create(message.channel, 'You already signed up silly!')
        new_character = Character.from_id(message.author.id)
        characters[message.author.id] = new_character
        await client.message_create(message.channel, f"Created a new user: {new_character}")


@Faito.commands
async def battle(client: Client, msg: Message):
    """
    Initiate a battle with a selected opponent
    :param client:
    :param msg:
    :return:
    """
    global characters, battles
    async with characters_lock:
        # just making sure no one is modifying the characters atm
        if msg.author.id not in characters:
            await client.message_create(msg.channel, "Create a character first please")
            return
        print(f'user mentions: {msg.user_mentions}')
        if len(msg.user_mentions) != 1:
            await client.message_create(msg.channel, "Mention a single user to start the battle with")
            return
        mentioned_user = msg.user_mentions[0]
        if mentioned_user.id not in characters:
            await client.message_create(msg.channel, "Make sure the opponent also has a user please")
            return
        new_battle = Battle.from_participants([characters[msg.author.id], characters[mentioned_user.id]])
        # todo make sure that we don't have an ongoing battle and all those edge cases
        battles.append(new_battle)
        embed = Embed(title="Battle started!", description=f"{msg.author.name} has challenged {mentioned_user.id} to "
                                                           f"a battle! May the best player win!")
        await client.message_create(msg.channel, embed=embed)
    await client.message_create()


# todo add cooldown per user
@Faito.commands
async def move(client, msg):
    """
    During a battle, do a move against the opponent
    :param client:
    :param msg:
    :return:
    """
    pass


@Faito.commands
async def reset(client, msg):
    """
    Reset the system (for ease of testing)
    :param client:
    :param msg:
    :return:
    """
    pass


@Faito.commands
async def save(client: Client, msg: Message):
    """
    Load the JSON
    :param client:
    :param msg:
    :return:
    """
    global characters
    async with characters_lock:
        with open('characters.json', 'w') as f:
            print(cattr.unstructure(characters))
            json.dump(cattr.unstructure(characters), f)
            await client.message_create(msg.channel, "Successfully saved the characters")


@Faito.commands
async def load(client: Client, msg: Message):
    """
    Load the JSON
    :param client:
    :param msg:
    :return:
    """
    global characters
    async with characters_lock:
        with open('characters.json') as f:
            data = json.load(f)
            characters = {k: cattr.structure(v, Character)
                          for k, v in data.items()}
            await client.message_create(msg.channel, "Successfully loaded the characters")


@Faito.commands
async def stats(client: Client, msg: Message):
    """
    Send the user's statistics
    :param client:
    :param msg:
    :return:
    """
    user = msg.author
    print(user.id)
    # todo get the actual stats
    stats = characters[msg.author.id]
    embed = Embed(title=f'Stats for {user.name}',
                  description="\n".join([f'{k.upper()}: {v}' for k, v in stats.items()]))
    await client.message_create(msg.channel,
                                embed=embed)


if __name__ == '__main__':
    Faito.start()
