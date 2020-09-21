from discord import Embed, Colour
from middleware.emojis.main import turn_country_ids_to_emojis


def create_top_embed(top_data: dict):
    # Add fields
    title = f"{top_data['map_name'].capitalize()} | Top {top_data['top_num']} {top_data['physics'].replace('-run','').upper()}"
    author = 'mDd records'
    url = top_data['url']
    top_embed = Embed(title=title, url=url, color=Colour(0x9FC1E4))
    map_levelshot_url = f"http://ws.q3df.org/images/levelshots/512x384/{top_data['map_name']}.jpg?fallback=1"
    top_embed.set_thumbnail(url=map_levelshot_url)
    top_embed.set_author(name=author)

    top_data['fields'] = format_top_data_fields(top_data['fields'])
    # join fields into one field
    top_data['table_rows'] = []
    for i in range(0, top_data['top_num']):
        top_data['table_rows'].append(' | '.join([field[i] for field in top_data['fields'].values()]) + ' |`')
    table = '\n'.join(top_data['table_rows'])
    top_embed.add_field(name='Records', value=table, inline=False)
    return top_embed


def format_top_data_fields(top_data_fields):
    for key, values in top_data_fields.items():
        max_value_length = len(max(values, key=len))
        formatted_values = []
        for value in values:
            padding = ' ' * (max_value_length - len(value))
            if key == 'players':
                value = value.replace('flag_??', 'pirate_flag')  # unknown flag to pirate flag
            formatted_values.append(value + padding)
        top_data_fields[key] = formatted_values
    return top_data_fields


def create_map_embed(map_data: dict):
    map_name, map_url, map_levelshot_url = [map_data[datum] for datum in ['name', 'url', 'levelshot_url']]
    map_embed = Embed(title=map_name, url=map_url, color=Colour(0xffffff))
    map_embed.set_image(url=map_levelshot_url)
    thumbnail_url = "https://ws.q3df.org/images/icons/32x32/defrag.png"
    map_embed.set_thumbnail(url=thumbnail_url)
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
            from mdd.top import get_wrs
            wr_data = get_wrs(map_name)
            for physics, wr_entry in wr_data.items():
                country_string = turn_country_ids_to_emojis([wr_entry['country']])[0].replace("flag_??", "pirate_flag")
                display_string = f"{country_string} {wr_entry['player']} [{wr_entry['time']}]"
                map_embed.add_field(name=f"{physics} record:", value=display_string, inline=True)
        except:
            pass

    return map_embed


def create_stats_embed(stats_data):
    # Add fields
    id, name, country = [stats_data.pop(datum) for datum in ['player_id', 'player_name', 'country']]
    country_string = turn_country_ids_to_emojis([country])[0].replace("flag_??", "pirate_flag")
    title = f"{country_string} {name} | Overall Statistics"
    author = 'mDd records'
    url = f"https://q3df.org/profil?id={id}"
    stats_embed = Embed(title=title, url=url, color=Colour(0x9FC1E4))
    stats_embed.set_thumbnail(url="http://ws.q3df.org/images/icons/32x32/bot_sarge.png")
    stats_embed.set_author(name=author)
    # join fields into one field
    for key, value in stats_data.items():
        field_name = key.replace('_', ' ').capitalize()
        stats_embed.add_field(name=field_name, value=value, inline=False)
    return stats_embed