import requests
from bs4 import BeautifulSoup
from random import randint
from settings import CONN_STRING
from sqlalchemy import create_engine


def get_random_map():
    num_maps = 9251
    random_row = randint(1, num_maps)
    db = create_engine(CONN_STRING)
    with db.connect() as conn:
        # Read
        select_statement = "SELECT map_nm, author, map_desc, rel_dt, phys_cd_str, func_cd_str, weap_cd_str, " \
                           "item_cd_str, func_cd_str " \
                           "FROM ws_maps " \
                           f"LIMIT 1 OFFSET {random_row}"
        result_set = conn.execute(select_statement)
        for r in result_set:
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


def get_map_data(map_name):
    url = f"http://ws.q3df.org/map/{map_name}/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    map_data = dict()
    map_data['name'] = map_name
    map_data['levelshot_url'] = 'https://ws.q3df.org'\
                            + soup.find('img', attrs={'id': 'mapdetails_levelshot'}).attrs['srcset']
    map_data['url'] = url
    map_data['fields'] = get_map_fields(soup)

    return map_data


def get_map_fields(map_soup):
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
