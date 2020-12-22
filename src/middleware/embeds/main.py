""" Handles embed creation and formatting """

from discord import Embed, Colour
from middleware.emojis.main import turn_country_ids_to_emojis


def create_top_embed(top_data: dict):
    """
    Creates embed for top records display
    :param top_data: dictionary of top records data containing necessary information for an embed
    :return: an embed displaying top records
    """

    # Metadata
    title = f"{top_data['map_name']} | Top {top_data['top_num']}"
    author = 'mDd records'
    url = top_data['url']
    map_levelshot_url = f"http://ws.q3df.org/images/levelshots/512x384/{top_data['map_name']}.jpg?fallback=1"

    top_embed = Embed(title=title, url=url, color=Colour(0x9FC1E4))
    top_embed.set_thumbnail(url=map_levelshot_url)
    top_embed.set_author(name=author)

    recs = format_recs(top_data["recs"])  # format records into an aesthetically-pleasing table

    physics_list = sorted(list(set([rec["physics"] for rec in recs])))  # each set of physics records

    for physics in physics_list:
        table_rows = []

        for rec in recs:
            if rec["physics"] == physics:
                table_rows.append(rec.pop("country") + "` " + " | ".join(rec[key] for key in rec.keys() if key != "physics") + ' |`')

        table = '\n'.join(table_rows)

        # Add fields (embed subsections)
        top_embed.add_field(name=f"Records ({physics.upper()})", value=table, inline=False)
    return top_embed


def format_recs(recs: list):
    """
    Helper function for formatting spacing and alignment of the records board table
    :param recs: Records data, including player name, time, and ranking.
    :return: Formatted version of records.
    """
    max_value_lengths = {}

    # Find all maximum value lengths
    for key in recs[0].keys():
        max_value_length = len(max([rec[key] for rec in recs], key=len))
        max_value_lengths[key] = max_value_length

    for rec in recs:
        for key in rec.keys():
            if key == "country":
                # Convert country IDs to flags:
                if rec["country"] == "null":
                    rec["country"] = ":pirate_flag:"
                else:
                    rec["country"] = f":flag_{rec['country'].lower()}:"
            else:
                # Add padding to fields where necessary
                rec[key] += " " * (max_value_lengths[key] - len(rec[key]))

    return recs


def create_map_embed(map_data: dict):
    """
    Creates embed for map information display
    :param map_data: Dictionary of data pertaining to a certain map
    :return: Embed displaying map information
    """
    map_name, map_url, map_levelshot_url = [map_data[datum] for datum in ['name', 'url', 'levelshot_url']]
    map_embed = Embed(title=map_name, url=map_url, color=Colour.from_rgb(155, 4, 52))
    map_embed.set_image(url=map_levelshot_url)
    thumbnail_url = "https://cdn.discordapp.com/attachments/788239274361356309/790741876285374544/defrag_3_40x40.png"
    map_embed.set_thumbnail(url=thumbnail_url, )
    map_embed.set_author(name="Worldspawn Archive")
    optional_fields = map_data['fields'].pop('optional', {})

    # Add optional embed fields
    for key, value in map_data['fields'].items():
        map_embed.add_field(name=key, value=value, inline=False if key == 'Author' else True)
    for key, value in optional_fields.items():
        value = value.replace(',', '')
        map_embed.add_field(name=key, value=value, inline=False)

    # Add world record data if map has the Timer function
    if 'Functions' in optional_fields and 'timer' in optional_fields['Functions'].lower():
        try:
            from mdd.records import get_wrs
            wr_data = get_wrs(map_name)
            for physics, wr_entry in wr_data.items():
                country_string = turn_country_ids_to_emojis([wr_entry['country']])[0].replace("flag_??", "pirate_flag")
                display_string = f"{country_string} {wr_entry['player']} [{wr_entry['time']}]"
                map_embed.add_field(name=f"{physics} record:", value=display_string, inline=True)
        except:
            pass

    return map_embed


def create_stats_embed(stats_data: dict):
    """
    Creates an embed for displaying an user's mdd statistics
    :param stats_data: Dictionary of mdd statistical data
    :return: An embed displaying a user's mdd statistics
    """

    # Embed metadata
    physics = stats_data.pop('physics') if 'physics' in stats_data else 'Overall'
    id, name, country = [stats_data.pop(datum) for datum in ['player_id', 'player_name', 'country']]
    country_string = turn_country_ids_to_emojis([country])[0].replace("flag_??", "pirate_flag")
    title = f"{country_string} {name} | {physics} Statistics"
    author = 'mDd records'
    url = f"https://q3df.org/profil?id={id}"

    # Create embed
    stats_embed = Embed(title=title, url=url, color=Colour(0x9FC1E4))
    stats_embed.set_thumbnail(url="http://ws.q3df.org/images/icons/32x32/bot_sarge.png")
    stats_embed.set_author(name=author)

    # Turn underscores into spaces, capitalize for field name display, add the field and its data.
    for key, value in stats_data.items():
        field_name = key.replace('_', ' ').capitalize()
        stats_embed.add_field(name=field_name, value=value, inline=False)
    return stats_embed
