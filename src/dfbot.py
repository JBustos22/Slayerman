from settings import CLIENT_TOKEN
import discord
from metadata import main as meta
from mdd import records as recs, user as usr
from mdd import mdd_scrape
from ws import maps
from middleware.emojis import main as ej
from middleware.embeds import main as emb
from profile import main as pf
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
        msg = None
        cmd = message.content.split(' ')[0]
        if not cmd[1:].isalnum():
            return
        discord_id = str(message.author.id)

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

                # Broken capitalization across q3df.org and ws.q3df.org
                map_name = map_name.lower()

                top_data = recs.get_top_from_db(top_num, map_name, physics)
                top_embed = emb.create_top_embed(top_data)
                return await message.channel.send(embed=top_embed)
            except Exception as e:
                msg = f"Huh? `usage: {meta.get_usage('top')}`"

        # elif cmd == "!wrs":
        #     try:
        #         map_name = message.content.split(' ')[1]
        #         msg = top.get_wrs(map_name)
        #     except:
        #         msg = f"Huh? `usage: {meta.get_usage('wrs')}`"

        elif cmd == '!myt':
            try:
                args = message.content.split(' ')[1:]
                map_name, physics = (args[0], args[1] + '-run') if len(args) == 2 else args + ['all']
                msg = usr.get_user_times(discord_id, map_name, physics)
            except Exception:
                msg = f"Huh? `usage: {meta.get_usage('myt')}`"

        elif cmd == '!mystats':
            try:
                args = message.content.split(' ')[1:]
                if len(args) > 0:
                    physics_string = args[0]
                    stats_data = usr.get_physics_user_stats(discord_id=discord_id, physics_string=physics_string)
                else:
                    stats_data = usr.get_overall_user_stats(discord_id=discord_id)
                stats_embed = emb.create_stats_embed(stats_data)
                return await message.channel.send(embed=stats_embed)
            except Exception as e:
                if str(e) in ("Invalid physics.", "No statistics found. Use !myid to check or set your mdd id."):
                    msg = e
                else:
                    msg = f"Huh? `usage: {meta.get_usage('mystats')}`"

        elif cmd == '!userstats':
            try:
                args = message.content.split(' ')[1:]
                mdd_id = int(args[0])
                if len(args) > 1:
                    physics_string = args[1]
                    stats_data = usr.get_physics_user_stats(physics_string, mdd_id=mdd_id)
                else:
                    stats_data = usr.get_overall_user_stats(mdd_id=mdd_id)
                stats_embed = emb.create_stats_embed(stats_data)
                return await message.channel.send(embed=stats_embed)
            except Exception as e:
                if str(e) in ("Invalid physics.", "No statistics found."):
                    msg = e
                else:
                    msg = f"Huh? `usage: {meta.get_usage('userstats')}`"

        elif cmd == '!random':
            try:
                args = message.content.split(' ')[1:]
                map_data = maps.get_random_map(args)
                emoted_fields = ej.turn_to_custom_emojis(guild=message.guild, **map_data['fields']['optional'])
                map_data['fields']['optional'] = emoted_fields
                map_embed = emb.create_map_embed(map_data)
                return await message.channel.send(' Random map:', embed=map_embed)
            except:
                msg = f"Huh? `usage: {meta.get_usage('random')}`"

        elif cmd == '!mapinfo':
            try:
                map_name = message.content.split(' ')[1]
                map_data = maps.get_map_data(map_name)
                emoted_fields = ej.turn_to_custom_emojis(guild=message.guild, **map_data['fields']['optional'])
                map_data['fields']['optional'] = emoted_fields
                map_embed = emb.create_map_embed(map_data)
                return await message.channel.send(embed=map_embed)
            except Exception as e:
                msg = f"Huh? `usage: {meta.get_usage('mapinfo')}`"

        elif cmd == '!newmap':
            try:
                if message.channel.type.name == 'news':
                    import re
                    from discord import Webhook
                    link = message.content.split(' ')[1]
                    map_r = r"https://ws.q3df.org/map/(.*)/"
                    map_name = re.match(map_r, link).group(1)
                    map_data = maps.get_map_data(map_name)
                    emoted_fields = ej.turn_to_custom_emojis(guild=message.guild, **map_data['fields']['optional'])
                    map_data['fields']['optional'] = emoted_fields
                    map_embed = emb.create_map_embed(map_data)
                    map_embed.set_image(url=map_embed.Empty)
                    for role in message.guild.roles:
                        if role.name == 'Maps subscribers':
                            mention = role.mention
                            await message.delete()
                            return await message.channel.send(f"{mention} New map: {map_name}", embed=map_embed)

                    await message.delete()
                    return await message.channel.send(f"New map: {map_name}", embed=map_embed)
            except:
                pass

        elif cmd == "!update":
            try:
                args = message.content.split(' ')[1:]

                for arg in args:
                    if arg in ["mdd", "records", "mdd_records_ranked"]:
                        await message.add_reaction("🔄")
                        mdd_scrape.crawl_records()
                        await message.remove_reaction("🔄", client.user)
                        await message.add_reaction("✅")

                return
            except Exception as e:
                await message.add_reaction("❌")
                msg = f"Huh? `usage: {meta.get_usage('update')}`"

        elif cmd == "!myid":
            try:
                args = message.content.split(' ')[1:]
                if len(args) > 0:
                    mdd_id = args[0]
                    msg = pf.set_id(discord_id, mdd_id)
                    if msg is None:
                        await message.add_reaction("✅")
                    else:
                        await message.add_reaction("❌")
                else:
                    msg = pf.get_id(message.author)
            except Exception:
                msg = f"Huh? usage: {meta.get_usage('myid')}"

        elif cmd == '!help':
            msg = meta.create_help_message()
            return await message.channel.send(msg)
        else:
            return

        if msg is not None:
            await message.channel.send(msg)

if __name__ == "__main__":
    client.run(CLIENT_TOKEN if len(sys.argv) == 1 else sys.argv[1])
