import requests
from bs4 import BeautifulSoup
# from tabulate import tabulate
from settings import CONN_STRING
from sqlalchemy import create_engine


def get_top(top_num: str, map_name: str, physics: str):
    physics_dict = {'vq3': '0', 'cpm': '1'}
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


def get_top_from_db(top_num: str, map_name: str, physics: str):
    physics_num = {'vq3': '0', 'cpm': '1'}[physics]
    top_num = abs(int(top_num))
    if top_num > 15:
        top_num = 15
    physics = physics + "-run" if physics == "cpm" else "vq3-run"
    recs_url = f'https://q3df.org/records/details?map={map_name}&mode=-1&physic={physics_num}'
    top_data = {'top_num': top_num, 'map_name': map_name, 'physics': physics, 'url': recs_url}
    top_fields = {
        'countries': [],
        'players': [],
        'times': [],
        'ranks': []
    }

    db = create_engine(CONN_STRING)

    with db.connect() as conn:
        # Read
        select_statement = "select country, player_name, time, player_pos, total_times " \
                           "from mdd_records_ranked " \
                           "where map_name=%s " \
                           "and physics=%s " \
                           "order by player_pos " \
                           "limit %s"
        replace_vars = (map_name, physics, str(top_num))
        result_set = conn.execute(select_statement, replace_vars)
        for r in result_set:
            top_fields['players'].append(" " + r.player_name)
            top_fields['countries'].append(r.country.lower())
            top_fields['times'].append(r.time)
            top_fields['ranks'].append(f"{r.player_pos}/{r.total_times}")

    top_data['fields'] = top_fields
    return top_data


def get_wrs(map_name: str):
    db = create_engine(CONN_STRING)

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

    return wr_data
