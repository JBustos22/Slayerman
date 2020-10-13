"""Processes data for commands relating to mdd time records. (e.g, !top and !wrs"""

import requests
from bs4 import BeautifulSoup
# from tabulate import tabulate
from settings import CONN_STRING
from sqlalchemy import create_engine


def get_top(top_num: str, map_name: str, physics: str):
    """
    Retrieves the top time records on a given map. This method scrapes the web instead of using the database.
    :param top_num: The max number of records to display (capped at 15)
    :param map_name: Name of the map for which top times are requested
    :param physics: Physics for which to show the time, if specified, otherwise returns all applicable physics
    :return: A dictionary containing top records data, to be formatted into an embed
    """
    physics_dict = {'vq3': '0', 'cpm': '1'}  # current mdd website specifies vq3 and cpm by 1 or 0
    top_num = str(abs(int(top_num))) if top_num.isnumeric() else '10'
    physics_num = physics_dict[physics]
    url = f'https://q3df.org/records/details?map={map_name}&mode=-1&physic={physics_num}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    top = soup.find('table', attrs={'class': 'recordlist'}).tbody.find_all('tr')
    max_recs = len(top)
    top_num = int(top_num) if int(top_num) < max_recs else max_recs
    top = soup.find('table', attrs={'class': 'recordlist'}).tbody.find_all('tr')[:top_num]
    top_data = {'top_num': top_num, 'map_name': map_name, 'physics': physics, 'url': url}
    top_fields = {
        'countries': [],
        'players': [],
        'times': [],
        'ranks': []
    }
    for rank in range(0, top_num):
        data = top[rank].find_all('td')[1:4]
        top_fields['players'].append(f"{data[0].text}")
        top_fields['countries'].append(data[0].next['title'])
        top_fields['times'].append(f"{data[1].text}")
        top_fields['ranks'].append(f"{data[2].text}")

    top_data['fields'] = top_fields
    return top_data


def get_top_from_db(top_num: str, map_name: str, physics: str = None):
    """
    Retrieves the top time records on a given map. This method queries the database for records.
    :param top_num: The max number of records to display (capped at 15)
    :param map_name: Name of the map for which top times are requested
    :param physics: Physics for which to show the time, if specified, otherwise returns all applicable physics
    :return: A dictionary containing top records data, to be formatted into an embed
    """

    top_num = abs(int(top_num))
    recs_url = f'https://q3df.org/records/details?map={map_name}&mode=-1'  # q3df.org page of the recorsd for embed use

    db = create_engine(CONN_STRING)

    with db.connect() as conn:
        recs = []

        # determines WHERE clause for the sql statement depending on whether physics were provided or not
        if physics is None:
            query_where = "WHERE map_name=%s"
            replace_vars = (map_name,)
        else:
            if physics in ["vq3", "cpm"]:
                physics += "-run"  # adds -run to vq3 and cpm for database compatibility

            query_where = "WHERE map_name=%s AND physics=%s"
            replace_vars = (map_name, physics)

        select_statement = "SELECT country, player_name, time, player_pos, total_times, physics " \
                           "FROM mdd_records_ranked " \
                           f"{query_where} " \
                           "ORDER by physics ASC, player_pos ASC"
        result_set = conn.execute(select_statement, replace_vars)

        for r in result_set:
            if r.player_pos <= top_num:
                rec_obj = {
                    "country" : r.country.lower(),
                    "player" : r.player_name,
                    "time" : r.time,
                    "rank" : f"{r.player_pos}/{r.total_times}",
                    "physics" : r.physics.replace("-run", "")
                }
                recs.append(rec_obj)
        result_set.close()

    top_data = {'top_num': top_num, 'map_name': map_name, 'url': recs_url, "recs" : recs}
    return top_data


def get_wrs(map_name: str):
    """
    Retrieves world record data for a specified map
    :param map_name: Name of map for which world records are requested
    :return: A dictionary of world record data to be formatted into an embed.
    """
    db = create_engine(CONN_STRING)
    map_name = map_name.lower()

    with db.connect() as conn:
        # Read
        select_statement = "select distinct on (physics) physics, country, player_name, time " \
                           "from mdd_records_ranked " \
                           "where map_name=%s " \
                           "and player_pos = 1 " \
                           "order by physics desc "
        replace_vars = (map_name,)
        result_set = conn.execute(select_statement, replace_vars)
        wr_data = {}
        for r in result_set:
            player, country, time, physics = r.player_name, r.country, r.time, r.physics.replace('-run', '')
            wr_data[physics.replace('-run', '')] = {"country": country, "player": player, "time": time}
        result_set.close()
    return wr_data
