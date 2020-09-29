from settings import CLIENT_TOKEN
import discord
from mdd import top, user as usr
from ws import maps
from middleware.emojis import main as ej
from middleware.embeds import main as emb
import sys


client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game("!help"))


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
                top_num, physics = (5, None)

                if len(args) == 1:
                    map_name = args[0]
                elif len(args) == 2:
                    if args[0].isdecimal():
                        top_num, map_name = args
                    else:
                        map_name, physics = args
                else:
                    top_num, map_name, physics = args

                top_data = top.get_top_from_db(top_num, map_name, physics)
                top_embed = emb.create_top_embed(top_data)
                return await message.channel.send(mention, embed=top_embed)
            except Exception as e:
                msg = "Huh? `usage: !top <[1-15](default 10)> <map> <physics>`"

        elif cmd == "!wrs":
            try:
                map_name = message.content.split(' ')[1]
                msg = top.get_wrs(map_name)
            except:
                msg = "Huh? ``usage: !wrs <map>``"

        elif cmd == '!myt':
            try:
                args = message.content.split(' ')[1:]
                map_name, physics = (args[0], args[1] + '-run') if len(args) == 2 else args + ['all']
                msg = usr.get_user_times(discord_id, map_name, physics)
            except Exception:
                msg = "Huh? `usage: !myt <map> <physics(opt)>`"

        elif cmd == '!mystats':
            try:
                args = message.content.split(' ')[1:]
                if len(args) > 0:
                    physics_string = args[0]
                    stats_data = usr.get_physics_user_stats(discord_id, physics_string)
                else:
                    stats_data = usr.get_overall_user_stats(discord_id)
                stats_embed = emb.create_stats_embed(stats_data)
                return await message.channel.send(mention, embed=stats_embed)
            except Exception as e:
                if str(e) in ("Invalid physics.", "No statistics found."):
                    msg = e
                else:
                    msg = "Huh? `usage: !mystats <physics (otp)>`"

        elif cmd == '!random':
            try:
                args = message.content.split(' ')[1:]
                map_data = maps.get_random_map(args)
                emoted_fields = await ej.turn_to_custom_emojis(guild=message.guild, **map_data['fields']['optional'])
                map_data['fields']['optional'] = emoted_fields
                map_embed = emb.create_map_embed(map_data)
                return await message.channel.send(mention + ' Random map:', embed=map_embed)
            except:
                msg = "Huh? `usage: !random`"

        elif cmd == '!mapinfo':
            try:
                map_name = message.content.split(' ')[1]
                map_data = maps.get_map_data(map_name)
                emoted_fields = await ej.turn_to_custom_emojis(guild=message.guild, **map_data['fields']['optional'])
                map_data['fields']['optional'] = emoted_fields
                map_embed = emb.create_map_embed(map_data)
                return await message.channel.send(mention, embed=map_embed)
            except Exception as e:
                msg = "Huh? `usage: !mapinfo <map>`"

        elif cmd == '!help':
            msg = "```---- !top\n" \
                    "Description: Get list of top times on a given map and physics.\n" \
                    "Usage: !top <[1-15](default 10)> <map> <physics>```" \
                    "```---- !myt\n" \
                    "Description: Get your times on a given map and physics.\n" \
                    "Both physics are searched if not specified.\n" \
                    "Usage: !myt <map> <physics(opt)>```" \
                    "```---- !mystats\n" \
                    "Description: Display various online stats about yourself. Defaults to overall if no physics\n" \
                    "Usage: !mystats <physics>```" \
                    "```---- !mapinfo\n" \
                    "Description: Get detailed map data.\n" \
                    "Usage: !mapinfo <map>```" \
                    "```---- !random\n" \
                    "Description: Present a random map.\n" \
                    "Usage: !random <args(opt)>\n" \
                    "Arguments: slick, strafe, weapon, long, good```"
            return await message.channel.send('{id}\n{message}'.format(id=mention, message=msg))
        else:
            return
        await message.channel.send('{id}\n{message}'.format(id=mention, message=msg))


client.run(CLIENT_TOKEN if len(sys.argv) == 1 else sys.argv[1])
