import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


def get_top(command: str):
    try:
        physics_dict = {'vq3': '0', 'cpm': '1'}
        command_parts = command.split(' ')
        if command_parts[0] != '!top':
            raise Exception
        top_num = command_parts[1]
        if not top_num.isnumeric():
            top_num = '10'
            map, physics_num = command_parts[1], physics_dict[command_parts[2]]
        else:
            map, physics_num = command_parts[2], physics_dict[command_parts[3]]
        r = requests.get(f'https://q3df.org/records/details?map={map}&mode=-1&physic={physics_num}')
        soup = BeautifulSoup(r.text, 'html.parser')
        top = soup.find('table', attrs={'class':'recordlist'}).tbody.find_all('tr')
        max_recs = len(top)
        if len(top_num) >= 1:
            top_num = int(top_num) if int(top_num) < max_recs else max_recs
        else:
            top_num = max_recs
        top = soup.find('table', attrs={'class': 'recordlist'}).tbody.find_all('tr')[:top_num]
        rows = []
        for rank in range(0, top_num):
            data = top[rank].find_all('td')[:4]
            date, player, time, standing = data[0].text, data[1].text, data[2].text, data[3].text
            rows.append([date, player, time, standing])
        return f"```{tabulate(rows, headers=['Date/Time', 'Player', 'Time', 'Rank'])}```"
    except Exception:
        return "Huh? `usage: !top <[1-15](default 10)> <map> <physics>`"