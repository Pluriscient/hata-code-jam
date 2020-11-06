from hata import Client
import json

from hata.discord.channel import message_relativeindex

secrets = json.load(open('secrets.json'))
Faito = Client(secrets['token'])

@Faito.events
async def ready(client):
    print(f'{client:f} logged in.')

@Faito.events
async def message_create(client, message):
    if message.author.is_bot:
        return
    
    if message.content == 'ping':
        await client.message_create(message.channel, 'pong')

    print(f'{client:f} logged in.')

Faito.start()