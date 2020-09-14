from settings import CLIENT_TOKEN, DB_PASSWORD
import discord
from mdd.top import get_top, get_wrs
from mdd.user import get_user_data
from ws.maps import get_random_map, get_map_data, create_map_embed
from middleware.emoji import main as ej
import sys


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
        elif cmd == "!wrs":
            try:
                map_name = message.content.split(' ')[1]
                msg = get_wrs(map_name)
            except:
                msg = "Huh? ``usage: !wrs <map>``"
        elif cmd == '!myt':
            try:
                args = message.content.split(' ')[1:]
                map_name, physics = args if len(args) == 2 else args + ['run']
                msg = get_user_data(discord_id, map_name, physics, db_pass=DB_PASSWORD)
            except Exception:
                msg = "Huh? `usage: !myt <map> <physics(opt)>`"
        elif cmd == '!random':
            try:
                map_name = get_random_map()
                map_data = get_map_data(map_name)
                emoted_fields = await ej.turn_to_emojis(guild=message.guild, **map_data['fields']['optional'])
                map_data['fields']['optional'] = emoted_fields
                map_embed = create_map_embed(map_data)
                return await message.channel.send(mention + ' Random map:', embed=map_embed)
            except:
                msg = "Huh? `usage: !random <map>`"
        elif cmd == '!mapinfo':
            try:
                map_name = message.content.split(' ')[1]
                map_data = get_map_data(map_name)
                is_df = "Timer" in map_data['fields']['optional']['Functions']
                emoted_fields = await ej.turn_to_emojis(guild=message.guild, **map_data['fields']['optional'])
                map_data['fields']['optional'] = emoted_fields
                map_embed = create_map_embed(map_data)
                # Add world record fields to maps with a timer
                if is_df:
                    map_embed.add_field(name = "World Records", value = get_wrs(map_name))
                return await message.channel.send(mention, embed=map_embed)
            except Exception as e:
                msg = "Huh? `usage: !mapinfo <map>`"
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

client.run(CLIENT_TOKEN if len(sys.argv) == 1 else sys.argv[1])
