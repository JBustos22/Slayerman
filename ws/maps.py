import requests
from bs4 import BeautifulSoup
from random import randint
from settings import CONN_STRING
from sqlalchemy import create_engine


def get_random_map(modes=[]):
    retry_limit = 300
    LONG_RECORDS = None

    db = create_engine(CONN_STRING)

    with db.connect() as conn:
        for retry_counter in range(0, retry_limit):
            # Get a random map
            if "long" in modes:
                if not LONG_RECORDS:
                    # Get a list of 1st place records that are longer than 3 minutes
                    # Choose a random record from this list, and present that record's map
                    select_statement = "SELECT *" \
                                        "FROM mdd_records_ranked " \
                                        "WHERE player_pos = 1" \
                                        "AND time_seconds > 180.0"

                    LONG_RECORDS = conn.execute(select_statement).fetchall()

                offset = randint(0, len(LONG_RECORDS) - 1)
                record_r = LONG_RECORDS[offset]

                map_name = record_r.map_name

                # Get map details
                # A problem can occur here where mdd_records_ranked contains a map,
                # but ws_maps doesn't.
                select_statement = "SELECT * " \
                                    "FROM ws_maps " \
                                    "WHERE map_nm = %s " \
                                    "LIMIT 1"
                replace_vars = (map_name)

                result_set = conn.execute(select_statement, replace_vars)
                r = result_set.first()
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

            if r == None:
                # DB issues, maybe incomplete ws_maps DB
                # My scraper didn't look for multiple .defi files per .pk3
                continue

            # Consider all selection modes
            failed = False

            for mode in modes:
                if mode == "good":
                    # Blacklist terms
                    blacklist = [
                        "nice",
                        "igoodmap",
                        "moko",
                        "marvin",
                        "gvn",
                        "baulo",
                        "govno",
                        "wesp",
                        "ass",
                        "fag",
                        "shit"
                    ]

                    if any(x in r.map_nm for x in blacklist):
                        failed = True
                        break

                    # TODO: Size > 2MB

                    # Number of records
                    select_statement = "SELECT *" \
                                        "FROM mdd_records_ranked " \
                                        "WHERE map_name=%s " \
                                        "ORDER BY time_seconds"
                    replace_vars = (r.map_nm)

                    result_set = conn.execute(select_statement, replace_vars)
                    total_records = result_set.rowcount

                    if total_records < 50:
                        failed = True
                        break

                    # Minimum time of 10 seconds
                    fastest_time = result_set.first().time_seconds

                    if fastest_time < 10.0:
                        failed = True
                        break

                elif mode == "strafe":
                    if r.weap_cd_str != None and any(wep in r.weap_cd_str for wep in ["Rocket Launcher", "Plasmagun", "Grenade Launcher", "Big Fucking Gun", "Lightning Gun"]):
                        failed = True
                        break

                elif mode == "weapon":
                    if r.weap_cd_str == None or not any(wep in r.weap_cd_str for wep in ["Rocket Launcher", "Plasmagun", "Grenade Launcher", "Big Fucking Gun", "Lightning Gun"]):
                        failed = True
                        break

                elif mode == "slick" or mode == "ice":
                    if not "Slick" in r.func_cd_str:
                        failed = True
                        break

                else:
                    # No restrictions
                    pass

            # Select another random map if current map does not fit modes
            if failed:
                continue

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
