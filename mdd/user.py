import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import psycopg2


def get_user_data(discord_id: str, df_map: str, physics: str, db_pass: str = 'password'):
    cur = psycopg2.connect(f"dbname=Defrag user=postgres password={db_pass}").cursor()
    query = 'SELECT mdd_id FROM users_ids WHERE discord_user = %s'
    cur.execute(query, (discord_id,))
    user_id = cur.fetchall()[0][0]
    url = f'https://q3df.org/profil?id={user_id}&s={df_map}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    times = soup.find('table', attrs={'class': 'recordlist'}).tbody.find_all('tr')
    rows = []
    if times[0].text != '\nno entries found...\n':
        for time in range(0, len(times)):
            data = times[time].find_all('td')[:5]
            date, map_name, time, standing, phys = [datum.text for datum in data[0:5]]
            if map_name.strip(' ') == df_map and physics in phys:
                rows.append([standing, time, phys, date])
        if len(rows) > 0:
            return f"```{tabulate(rows, headers=['Rank', 'Time', 'Physics', 'Date/Time'])}```"
        else:
            return f"You have no{'' if physics=='run' else ' ' + physics} time on this map"
    else:
        return f"No mDd records found on {df_map}."
