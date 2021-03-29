""" Handles data retrieval and processing of Worldspawn map data """

import requests
from bs4 import BeautifulSoup
from random import randint
from settings import db


def get_random_map(modes=[]):
    """
    Fetches a random map corresponding with mode filters if provided
    :param modes: Descriptive filters to narrow down the search, i.e strafe for strafe-only, etc.
    :return: Map data dictionary corresponding to the resulting map
    """

    with db.connect() as conn:
        QUERY_PARAMS = []

        if "slick" in modes:
            QUERY_PARAMS.append("func_slick_flg = B'1'")
        if "weapon" in modes:
            QUERY_PARAMS.append("(weap_gl_flg = B'1' OR weap_rl_flg = B'1' OR weap_pg_flg = B'1' OR weap_bf_flg = B'1')")
        if "strafe" in modes:
            QUERY_PARAMS.append("(weap_gl_flg = B'0' AND weap_rl_flg = B'0' AND weap_pg_flg = B'0' AND weap_bf_flg = B'0')")
        if "long" in modes:
            # TODO: How to make sure that all physics are long?
            QUERY_PARAMS.append("map_nm IN (SELECT DISTINCT map_name FROM mdd_records_ranked WHERE player_pos = 1 AND time_seconds > 150.0 AND physics = 'cpm-run')")
        if "deluxe" in modes:
            # Blacklist
            # Friendly reminder that all % wildcards must be doubled
            # to avoid python tomfoolery
            blacklist = [
                "nice%%",
                "igoodmap%%",
                "moko%%",
                "marvin%%",
                "%%gvn%%",
                "baulo%%",
                "govno%%",
                "%%wesp%%",
                "%%ass%%",
                "%%fag%%",
                "%%shit%%",
                "line#%%"
            ]

            blacklist_s = " AND ".join(f"map_nm NOT LIKE '{x}'" for x in blacklist)

            # 50 Records (caveat: total_times is per physics, so maybe a lower value of 35-40 is better here for CPM only)
            num_records_s = "map_nm IN (SELECT DISTINCT map_name FROM mdd_records_ranked WHERE total_times > 40)"

            # Minimum time of 10 seconds
            min_time_s = "map_nm NOT IN (SELECT DISTINCT map_name FROM mdd_records_ranked WHERE player_pos = 1 AND time_seconds < 10.0)"

            # TODO Maybe use INTERSECT for these

            QUERY_PARAMS.append(blacklist_s)
            QUERY_PARAMS.append(num_records_s)
            QUERY_PARAMS.append(min_time_s)

        if len(QUERY_PARAMS) > 0:
            QUERY_WHERE = "WHERE " + " AND ".join(QUERY_PARAMS)

            select_statement = "SELECT map_nm, author, map_desc, rel_dt, phys_cd_str, func_cd_str, weap_cd_str, " \
                               "item_cd_str, func_cd_str " \
                               "FROM ws_maps " \
                               + QUERY_WHERE

            result_set = conn.execute(select_statement)
            result_rows = result_set.fetchall()

            offset = randint(0, len(result_rows) - 1)
            r = result_rows[offset]
            result_set.close()

        else:
            num_maps = 9251
            offset = randint(1, num_maps)

            # Read
            select_statement = "SELECT map_nm, author, map_desc, rel_dt, phys_cd_str, func_cd_str, weap_cd_str, " \
                               "item_cd_str, func_cd_str " \
                               "FROM ws_maps " \
                               f"LIMIT 1 OFFSET {offset}"
            result_set = conn.execute(select_statement)
            r = result_set.first()
            result_set.close()

        map_name = r.map_nm
        url = f"http://ws.q3df.org/map/{map_name}/"
        map_data = dict()
        map_data['name'] = map_name
        map_data['levelshot_url'] = f"https://ws.q3df.org/images/levelshots/512x384/{map_name}.jpg?fallback=1"
        map_data['url'] = url
        fields = dict()
        fields['Author'] = r.author
        fields['Description'] = r.map_desc
        fields['Release Date'] = str(r.rel_dt)
        fields['Physics'] = r.phys_cd_str
        opt_fields = {"Weapons": r.weap_cd_str, "Items": r.item_cd_str, "Functions": r.func_cd_str}
        opt_fields = {key: val for key, val in opt_fields.items() if val != None}  # remove None
        fields['optional'] = opt_fields
        map_data['fields'] = fields
        map_data = {key: val for key, val in map_data.items() if val != None}  # remove None
        return map_data


def get_map_data(map_name: str):
    """
    Retrieves descriptive data about a specific map
    :param map_name: The name of the map
    :return: Map data dictionary containing the map's information, to be later formatted into an embed
    """
    url = f"http://ws.q3df.org/map/{map_name}/"
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    map_data = dict()
    map_data['name'] = map_name
    map_data['levelshot_url'] = f"https://ws.q3df.org/images/levelshots/512x384/{map_name}.jpg?fallback=1"
    map_data['url'] = url
    map_data['fields'] = get_map_fields(soup)

    return map_data


def get_map_fields(map_soup):
    """
    Retrieves map data that will live in the embed as a 'field'. Some of these can be optional (like 'Weapons')
    :param map_soup: BS4 soup object containing the map page's html from Worldspawn
    :return: A dictionary of fields and the data that will go under each of them
    """
    fields = dict()
    map_data_table = map_soup.find("table", {"id": "mapdetails_data_table"})

    # Author (optional)
    try:
        fields['Author'] = map_data_table.find("td", string="Author").parent.find("a").text
    except:
        fields['Author'] = "Unknown"
    # Description (optional)
    try:
        fields['Description'] = map_data_table.find("td", string="Mapname").next_sibling.text
    except:
        pass
    # Release Date (mandatory)
    fields['Release Date'] = map_data_table.find("td", string="Release date").next_sibling.text
    # Physics (optional)
    try:
        physics = [field.text for field in map_data_table.find("td", string="Defrag physics").parent.find_all("a")]
        fields['Physics'] = ', '.join(physics)
    except:
        pass

    # Optional image-based fields:
    opt = dict()
    opt_keys = ["Weapons", "Items", "Functions"]

    for key in opt_keys:
        try:
            data_list = [img["title"] for img in map_data_table.find("td", string=key).parent.find_all("img")]
            data_string = ', '.join(data_list)
            opt[key] = data_string
        except:
            pass
    fields['optional'] = opt

    return fields
