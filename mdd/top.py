import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


def get_top(top_num: str, map_name: str, physics: str):
    top_num = str(abs(int(top_num))) if top_num.isnumeric() else '10'
    physics_num = '1' if physics == 'cpm' else '0'
    url = f'https://q3df.org/records/details?map={map_name}&mode=-1&physic={physics_num}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    top = soup.find('table', attrs={'class': 'recordlist'}).tbody.find_all('tr')
    max_recs = len(top)
    top_num = int(top_num) if int(top_num) < max_recs else max_recs
    top = soup.find('table', attrs={'class': 'recordlist'}).tbody.find_all('tr')[:top_num]
    rows = []
    for rank in range(0, top_num):
        data = top[rank].find_all('td')[:4]
        date, player, time, standing = data[0].text, data[1].text, data[2].text, data[3].text
        rows.append([date, player, time, standing])
    return f"```{tabulate(rows, headers=['Date/Time', 'Player', 'Time', 'Rank'])}```"
