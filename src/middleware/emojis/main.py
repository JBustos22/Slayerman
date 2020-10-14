""" Handles emoji transformations and usage """

from middleware.config import png_dict


def turn_country_ids_to_emojis(country_id_list: list):
    """
    Turns a list of country ids (de, se, uk, etc.) into flag emojis (:flag_de:, ...). If missing, use :flag_??:
    :param country_id_list: List of country ids, usually corresponding to players for record display
    :return: A list of flag emoji strings
    """
    country_emoji_list = []
    for country_id in country_id_list:
        country_id = country_id.lower()
        emoji_string = f":flag_{country_id}:" if country_id not in ('null', '') else ':flag_??:'
        country_emoji_list.append(emoji_string)
    return country_emoji_list


def turn_to_custom_emojis(guild, **original_dict):
    """
    If the emojis are available, turns objects such as weapons, items, or functions into its corresponding emoji strings
    :param guild: The discord server at which the current instance of the bot lives
    :param original_dict: Dictionary containing the weapons, iterms, and/or functions are simple strings
    :return: The original dictionary passed in, with all applicable emoji replacements
    """
    for category, objects in original_dict.items():
        custom_emojis = get_custom_emojis(guild, category, objects)
        for object, emoji in custom_emojis.items():
            emoji_string = str(emoji)
            original_dict[category] = original_dict[category].replace(object, emoji_string)  # replace with emoji string
    return original_dict


def get_custom_emojis(guild, category: str, objects: str):
    """
    Searches the discord server for existing custom emojis whose names match certain keywords
    :param guild: The discord server in which the current bot instance lives
    :param category: Category of object, i.e Weapons, Items, or Functions
    :param objects: A comma-separated list of objects under the current category, i.e 'Slick, Teleporter, Timer'
    :return: A dictionary of custom emojis matching object values
    """
    custom_emojis = dict()
    for object in objects.split(', '):
        try:
            emoji_name = png_dict[category][object]  # Get mapping from string name -> emoji identifier
            for emoji in guild.emojis:
                if emoji_name == emoji.name:  # This emoji exists on the server
                    custom_emojis[object] = emoji
        except Exception:
            pass
    return custom_emojis
