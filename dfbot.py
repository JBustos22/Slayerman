import discord
from mdd.top import get_top
from mdd.user import get_user_data
from ws.maps import get_random_map, get_map_details
from settings import CLIENT_TOKEN, DB_PASSWORD

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!'):
        cmd = message.content.split(' ')[0]
        if not cmd[1:].isalnum():
            return
        discord_id = str(message.author)
        mention = message.author.mention
        if cmd == '!top':
            reply = get_top(message.content)
            return await message.channel.send('{id}\n{message}'.format(id=mention, message=reply))
        elif cmd == '!myt':
            try:
                msg_parts = message.content.split(' ')
                command, map = msg_parts[0:2]
                physics = msg_parts[2] if len(msg_parts) == 3 else 'run'
                reply = get_user_data(discord_id, map, physics, DB_PASSWORD)
            except Exception:
                reply = "Huh? `usage: !myt <map> <physics(opt)>`"
        elif cmd == '!random':
            reply = get_random_map()
            return await message.channel.send('{id}\n{message}'.format(id=mention, message=reply))
        elif cmd == '!details':
            try:
                map = message.content.split(' ')[1]
                reply = get_map_details(map)
                return await message.channel.send(mention, embed=reply)
            except Exception:
                reply = "Something went wrong."
        elif cmd == '!help':
            reply = "\n**top**\n```" \
                    "Description: Get list of top times on a given map and physics.\n" \
                    "Usage: !top <[1-15](default 10)> <map> <physics>```\n" \
                    "**myt**\n```" \
                    "Description: Get your times on a given map and physics. " \
                    "Both physics are searched if not specified.\n" \
                    "Usage: !myt <map> <physics(opt)>```\n" \
                    "**random**\n```" \
                    "Description: Generate a random map.\n" \
                    "Usage: !random (more params to come)```\n" \
                    "**details**\n```" \
                    "Description: Get detailed map data.\n" \
                    "Usage: !details <map>```\n"
            return await message.channel.send('{id}\n{message}'.format(id=mention, message=reply))
        else:
            reply = 'Command not recognized. use !help for a list of commands.'
        await message.channel.send('{id}\n{message}'.format(id=mention, message=reply))

client.run(CLIENT_TOKEN)
