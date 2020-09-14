from discord import Embed, Colour


def create_top_embed(top_data: dict):
    # Add fields
    title = f"Top {top_data['top_num']} {top_data['physics']} times on {top_data['map_name']}"
    author = 'mDd records'
    url = top_data['url']
    top_embed = Embed(title=title, url=url, color=Colour(0x9FC1E4))
    thumbnail_url = "https://q3df.org/Views/frontend/_resources/images/logo.png"
    top_embed.set_thumbnail(url=thumbnail_url)
    top_embed.set_author(name=author)
    for key, value_list in top_data['fields'].items():
        values = '\n'.join(value_list)
        top_embed.add_field(name=key, value=values, inline=True)
    return top_embed


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
            map_embed.add_field(name='World Records', value=get_wrs(map_name))
        except:
            pass

    return map_embed