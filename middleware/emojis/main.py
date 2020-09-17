from middleware.config import png_dict


def turn_country_ids_to_emojis(country_id_list):
    country_emoji_list = []
    for country_id in country_id_list:
        emoji_string = f":flag_{country_id}:" if country_id != 'null' else ':flag_??:'
        country_emoji_list.append(emoji_string)
    return country_emoji_list


async def turn_to_custom_emojis(guild, **original_dict):
    for category, objects in original_dict.items():
        custom_emojis = await create_custom_emojis(guild, category, objects)
        for object, emoji in custom_emojis.items():
            emoji_string = str(emoji)
            original_dict[category] = original_dict[category].replace(object, emoji_string)
    return original_dict


async def create_custom_emojis(guild, category, objects):
    custom_emojis = dict()
    for object in objects.split(', '):
        try:
            emoji_name = png_dict[category][object]
            for emoji in guild.emojis:
                if emoji_name == emoji.name:
                    custom_emojis[object] = emoji
        except Exception:
            pass
    return custom_emojis
