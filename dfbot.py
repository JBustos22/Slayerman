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
            try:
                args = message.content.split(' ')[1:]
                top, map_name, physics = args if len(args) == 3 else ['10'] + args
                msg = get_top(top, map_name, physics)
            except Exception:
                msg = "Huh? `usage: !top <[1-15](default 10)> <map> <physics>`"
        elif cmd == '!myt':
            try:
                args = message.content.split(' ')[1:]
                map_name, physics = args if len(args) == 2 else args + ['run']
                msg = get_user_data(discord_id, map_name, physics, db_pass=DB_PASSWORD)
            except Exception:
                msg = "Huh? `usage: !myt <map> <physics(opt)>`"
        elif cmd == '!random':
            msg = get_random_map()
        elif cmd == '!mapinfo':
            try:
                map_name = message.content.split(' ')[1]
                map_embed = get_map_details(map_name)
                return await message.channel.send(mention, embed=map_embed)
            except Exception:
                msg = "Huh? `usage: !mapinfo <map>"
        elif cmd == '!help':
            msg = "\n**top**\n```" \
                    "Description: Get list of top times on a given map and physics.\n" \
                    "Usage: !top <[1-15](default 10)> <map> <physics>```\n" \
                    "**myt**\n```" \
                    "Description: Get your times on a given map and physics. " \
                    "Both physics are searched if not specified.\n" \
                    "Usage: !myt <map> <physics(opt)>```\n" \
                    "**random**\n```" \
                    "Description: Generate a random map.\n" \
                    "Usage: !random (more params to come)```\n" \
                    "**mapinfo**\n```" \
                    "Description: Get detailed map data.\n" \
                    "Usage: !mapinfo <map>```\n"
            return await message.channel.send('{id}\n{message}'.format(id=mention, message=msg))
        else:
            msg = 'Command not recognized. use !help for a list of commands.'
        await message.channel.send('{id}\n{message}'.format(id=mention, message=msg))

client.run(CLIENT_TOKEN)
