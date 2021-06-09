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
import time
from servers import main as sv
from datetime import datetime

client = discord.Client()
UPDATE_TIME = None
UPDATE_TIME_MAPS = datetime.now().timestamp()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game("!help"))
    last_check = datetime.min

    q3df_sv_id = 751483934034100274 #649454774785146894
    q3df_guild = client.get_guild(q3df_sv_id)

    demand_ch_id = 820036524900614174 #820057557473165382
    demand_channel = q3df_guild.get_channel(demand_ch_id)

    alert_ch_id = 751568522982719588 #822853096165736458
    alert_channel = q3df_guild.get_channel(alert_ch_id)

    max_inactivity = 3
    while True:
        try:
            active_servers = sv.scrape_servers_data()
            if active_servers['update_time'] > last_check:
                last_check = active_servers['update_time']
                for ip in SERVERS:
                    if SERVERS[ip]['server_id'] in active_servers:  # one of our servers is active
                        server_id = SERVERS[ip]['server_id']
                        if active_servers[server_id]['players_qty'] == 0:
                            SERVERS[ip]['inactivity_count'] += 1
                            sv.update_json('servers', SERVERS)
                            print(
                                f"Server {SERVERS[ip]['hostname']} inactivity detected. {SERVERS[ip]['inactivity_count']}/{max_inactivity}")
                            if SERVERS[ip]['inactivity_count'] >= max_inactivity:
                                SERVERS[ip]['inactivity_count'] = 0
                                print(f"Stopping server {SERVERS[ip]['hostname']} due to inactivity")
                                message = await demand_channel.fetch_message(SERVERS[ip]['message_id'])
                                await stop_server(message, ip, inactivity=True)
                                sv.update_json('servers', SERVERS)
                                await alert_channel.send(
                                    content=f":flag_{SERVERS[ip]['flag']}: `{SERVERS[ip]['hostname']}` was stopped due to inactivity.")
                        else:
                            SERVERS[ip]['inactivity_count'] = 0  # reset inactivity counter
                            sv.update_json('servers', SERVERS)
                            print(
                                f"Server {SERVERS[ip]['hostname']} activity detected. Inactivity count reset to {SERVERS[ip]['inactivity_count']}")

        except Exception as e:
            print("Failed auto-stopper due to: ", e)
            time.sleep(10)

        # New maps
        if datetime.now().timestamp() - UPDATE_TIME_MAPS > 600:
            maps_new = get_newmaps()

            for map_url in maps_new:
                try:
                    import re
                    from discord import Webhook
                    map_r = r"https://ws.q3df.org/map/(.*)/"
                    map_name = re.match(map_r, map_url).group(1)
                    map_data = maps.get_map_data(map_name)
                    emoted_fields = ej.turn_to_custom_emojis(guild=q3df_guild, **map_data['fields']['optional'])
                    map_data['fields']['optional'] = emoted_fields
                    map_embed = emb.create_map_embed(map_data)
                    map_embed.set_image(url=map_embed.Empty)

                    for role in q3df_guild.roles:
                        if role.name == 'Maps subscribers':
                            mention = role.mention
                            await alert_channel.send(f"{mention} New map: {map_name}", embed=map_embed)
                except Exception as e:
                    print("Failed to fetch new maps due to: ", e)

        await asyncio.sleep(60)


@client.event
async def on_message(message):
    global UPDATE_TIME
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
                top_embed = emb.create_top_embed(top_data, UPDATE_TIME)
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
                stats_embed = emb.create_stats_embed(stats_data, UPDATE_TIME)
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
                stats_embed = emb.create_stats_embed(stats_data, UPDATE_TIME)
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
            pass
            '''
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
            '''

        # elif cmd == "!update":
        #     try:
        #         args = message.content.split(' ')[1:]
        #
        #         for arg in args:
        #             if arg in ["mdd", "records", "mdd_records_ranked"]:
        #                 await message.add_reaction("🔄")
        #                 mdd_scrape.crawl_records()
        #                 await message.remove_reaction("🔄", client.user)
        #                 await message.add_reaction("✅")
        #
        #         return
        #     except Exception as e:
        #         await message.add_reaction("❌")
        #         msg = f"Huh? `usage: {meta.get_usage('update')}`"

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

        elif cmd == "!listservers" and message.author.guild_permissions.administrator:
            global SERVERS
            await message.delete()
            await message.channel.purge(limit=len(SERVERS))
            for ip, metadata in SERVERS.items():
                embed = sv.create_server_embed(ip, metadata)
                server_msg = await message.channel.send(embed=embed)
                if SERVERS[ip]['status'] == 'Stopped':
                    await server_msg.add_reaction("▶️")
                elif SERVERS[ip]['status'] == 'Active':
                    await server_msg.add_reaction("⏹️")
                SERVERS[ip]['message_id'] = server_msg.id
                time.sleep(0.3)
            sv.update_json('servers', SERVERS)

        elif cmd == '!help':
            msg = meta.create_help_message()
            return await message.channel.send(msg)
        else:
            return

        if msg is not None:
            await message.channel.send(msg)


@client.event
async def on_raw_reaction_add(payload):
    global SERVERS
    global ACTIVATORS
    demand_ch_id = 820036524900614174
    alert_ch_id = 751568522982719588
    if payload.user_id == client.user.id:
        return
    for ip, metadata in SERVERS.items():
        if payload.message_id == SERVERS[ip]['message_id']:
            channel = payload.member.guild.get_channel(demand_ch_id)  #get server-on-demand channel
            alert_channel = payload.member.guild.get_channel(alert_ch_id)
            message = await channel.fetch_message(payload.message_id)
            if SERVERS[ip]['status'] == 'Stopped' and payload.emoji.name == '▶️':
                if str(payload.user_id) in ACTIVATORS:
                    await message.remove_reaction(payload.emoji, payload.member)
                    activated_ip = ACTIVATORS[str(payload.user_id)]
                    dm_channel = await payload.member.create_dm()
                    return await dm_channel.send(
                        content=f"You cannot start {SERVERS[ip]['hostname']} because you"
                                f" already started {SERVERS[activated_ip]['hostname']}. Please stop that server "
                                f"before starting a new one.")
                server_url = sv.get_df_launcher_url(ip, SERVERS[ip]['region'])
                await launch_server(payload, message, ip)
                ACTIVATORS[str(payload.user_id)] = ip
                sv.update_json("activators", ACTIVATORS)
                print(f"Added {payload.user_id} to activators. activators = {ACTIVATORS}")
                activator_name = payload.member.nick if payload.member.nick is not None else payload.member.name
                await alert_channel.send(
                    content=f"{activator_name} ({SERVERS[ip]['activator_dc']}) has started :flag_{SERVERS[ip]['flag']}: "
                            f"`{SERVERS[ip]['hostname']} ({SERVERS[ip]['flag']}.q3df.run)`. Connect: {server_url}")
                dm_channel = await payload.member.create_dm()
                await dm_channel.send(content=f"You have started {SERVERS[ip]['hostname']}!"
                                              f" Connect to it using `/connect {ip}` in your defrag engine, "
                                              f"or if you have the Defrag Launcher, click {server_url}."
                                              f" As a courtesy to the server hoster, "
                                              f"please stop the server by reacting with :stop_button: on the "
                                              f"server's embed if you are done with it and the server is empty. "
                                              f"If there are any issues with the server, please contact frog/h@des "
                                              f"(frog#1459) through discord. Enjoy!")
                return
            if SERVERS[ip]['status'] == 'Active' and payload.emoji.name == '⏹️':
                if payload.user_id != SERVERS[ip]['activator'] and not payload.member.permissions_in(
                        channel).manage_channels:
                    await message.remove_reaction(payload.emoji, payload.member)
                    dm_channel = await payload.member.create_dm()
                    return await dm_channel.send(
                        content=f"You do not have permission to stop {SERVERS[ip]['hostname']}, as you did not start the server. ")
                await stop_server(message, ip, payload)
                stopper_name = payload.member.nick if payload.member.nick is not None else payload.member.name
                await alert_channel.send(
                    content=f"{stopper_name} ({payload.member.name}#{payload.member.discriminator}) has stopped :flag_{SERVERS[ip]['flag']}: `{SERVERS[ip]['hostname']}`")
                return


async def launch_server(payload, message, ip):
    global ACTIVATORS
    global SERVERS
    await message.clear_reactions()
    embed = message.embeds[0]
    embed.set_field_at(1, name='Status', value=f':orange_circle: Starting', inline=False)
    await message.edit(embed=embed)
    sv.start_server(SERVERS[ip])
    embed = message.embeds[0]
    embed.set_field_at(1, name='Status', value=f':green_circle: Active', inline=False)
    SERVERS[ip]['status'] = "Active"
    SERVERS[ip]['activator'] = payload.user_id
    SERVERS[ip]['activator_dc'] = f"{payload.member.name}#{payload.member.discriminator}"
    embed.add_field(name="Activator", value=f"{payload.member.mention}", inline=False)
    sv.update_json("servers", SERVERS)
    await message.edit(embed=embed)
    await message.add_reaction("⏹️")


async def stop_server(message, ip, payload=None, inactivity=False):
    global SERVERS
    global ACTIVATORS
    await message.clear_reactions()
    embed = message.embeds[0]
    try:
        embed.set_field_at(1, name='Status', value=f':orange_circle: Stopping', inline=False)
        if inactivity:
            embed.set_field_at(2, name='Reason', value=f"Inactivity", inline=False)
        else:
            embed.set_field_at(2, name='Stopper', value=f"{payload.member.mention}", inline=False)
    except:
        pass
    await message.edit(embed=embed)
    time.sleep(10)
    sv.stop_server(SERVERS[ip])
    SERVERS[ip]['status'] = "Stopped"
    SERVERS[ip]['inactivity_counter'] = 0
    embed = message.embeds[0]
    embed.remove_field(2)
    embed.set_field_at(1, name='Status', value=':red_circle: Stopped', inline=False)
    await message.edit(embed=embed)
    await message.add_reaction("▶️")
    try:
        ACTIVATORS.pop(str(SERVERS[ip]['activator']))
        print(f"Removed {SERVERS[ip]['activator']} from activators. activators = {ACTIVATORS}")
    except KeyError:
        pass
    sv.update_json("activators", ACTIVATORS)
    SERVERS[ip]['activator'] = ""
    SERVERS[ip]['activator_dc'] = ""
    sv.update_json('servers', SERVERS)


def auto_update(minutes=2):
    from datetime import datetime
    global UPDATE_TIME

    while True:
        try:
            mdd_scrape.crawl_records()
            UPDATE_TIME = datetime.now()
            time.sleep(60 * minutes)
        except:
            pass
            time.sleep(20)

def get_newmaps():
    import feedparser

    from datetime import datetime
    from dateutil.parser import parse as parse_dateutil

    global UPDATE_TIME_MAPS

    if UPDATE_TIME_MAPS == None:
        UPDATE_TIME_MAPS = datetime.now().timestamp()

    maps_new = []

    try:
        maps_feed = feedparser.parse("https://ws.q3df.org/rss/released_maps/")

        for map in maps_feed.entries:
            map_url = map.link
            map_release_ts = parse_dateutil(map.published).timestamp()

            if map_release_ts > UPDATE_TIME_MAPS:
                maps_new.append(map_url)

        UPDATE_TIME_MAPS = datetime.now().timestamp()
    except Exception as e:
        print("Failed to fetch WS RSS due to: ", e)

    return maps_new


if __name__ == "__main__":
    import json
    import threading
    import asyncio

    with open('servers/servers.json') as f:
        SERVERS = json.loads(f.read())
    with open("servers/activators.json") as f:
        ACTIVATORS = json.loads(f.read())

    threading.Thread(target=auto_update, daemon=True).start()
    client.run(CLIENT_TOKEN if len(sys.argv) == 1 else sys.argv[1])
