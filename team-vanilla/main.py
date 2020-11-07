from hata import Client
import json
from hata.ext.commands import setup_ext_commands
from character import Character


secrets = json.load(open('secrets.json'))
Faito = Client(secrets['token'])
setup_ext_commands(Faito, '!')


@Faito.events
async def ready(client):
    print(f'{client:f} logged in.')


@Faito.commands
async def ping(client, message):
    await client.message_create(message.channel, 'pong')


from hata import KOKORO, Lock, enter_executor
FILE_LOCK = Lock(KOKORO)

@Faito.commands
async def signup(client, message):
    if message.author.is_bot:
        return

    async with FILE_LOCK:
        async with enter_executor():

            with open('data.json', 'r') as jsonFile:
                data = json.load(jsonFile)

            if str(message.author.id) in data["players"]:
                previously_signed_up = True
            else:
                previously_signed_up = False
                new_character = Character(message.author.id)
                data["players"][str(message.author.id)] = new_character.json_stats()

            with open('data.json', 'w') as jsonFile:
                json.dump(data, jsonFile)

    # the await here seems to have to be outside the FILE_LOCK & enter_executor asyncs above (not sure why)
    if previously_signed_up:
        await client.message_create(message.channel, 'You already signed up silly!')




import signal
from threading import main_thread
from hata import CLIENTS
import os
import threading
sigmap = {signal.SIGINT: signal.CTRL_C_EVENT,
              signal.SIGBREAK: signal.CTRL_BREAK_EVENT}

def kill(pid, signum):
        if signum in sigmap and pid == os.getpid():
            # we don't know if the current process is a
            # process group leader, so just broadcast
            # to all processes attached to this console.
            pid = 0
        thread = threading.current_thread()
        handler = signal.getsignal(signum)
        # work around the synchronization problem when calling
        # kill from the main thread.
        if (signum in sigmap and
            thread.name == 'MainThread' and
            callable(handler) and
            pid == 0):
            event = threading.Event()
            def handler_set_event(signum, frame):
                event.set()
                return handler(signum, frame)
            signal.signal(signum, handler_set_event)                
            try:
                os.kill(pid, sigmap[signum])
                # busy wait because we can't block in the main
                # thread, else the signal handler can't execute.
                while not event.is_set():
                    pass
            finally:
                signal.signal(signum, handler)
        else:
            os.kill(pid, sigmap.get(signum, signum))

@Faito.commands
async def shutdown(client, message):
    
    for client_ in CLIENTS:
        await client_.disconnect()
    
    await client.message_create(message.channel, 'Clients stopped, stopping process.')
    client.loop.stop()
    thread_id = main_thread().ident

    kill(thread_id, signal.SIGTERM)


Faito.start()