import requests
from bs4 import BeautifulSoup
from tabulate import tabulate


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
        'Rank': [],
        'countries': [],
        'Player': [],
        'Time': [],
    }
    for rank in range(0, top_num):
        data = top[rank].find_all('td')[1:4]
        top_fields['Player'].append(data[0].text)
        top_fields['countries'].append(data[0].next['title'])
        top_fields['Time'].append(data[1].text)
        top_fields['Rank'].append(data[2].text)

    top_data['fields'] = top_fields
    return top_data

def get_wrs(map_name: str):
    rows = []

    for physics_num in [0,1]:
        url = f'https://q3df.org/records/details?map={map_name}&mode=-1&physic={physics_num}'
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        try:
            top = soup.find('table', attrs={'class': 'recordlist'}).tbody.find_all('tr')[0]
            data = top.find_all('td')[:4]
            physics = 'vq3' if physics_num == 0 else 'cpm'
            date, player, time = data[0].text, data[1].text, data[2].text
            rows.append([physics, player, time])
        except Exception:
            continue

    return f"```{tabulate(rows, headers=['Physics', 'Player', 'Time'])}```" if len(rows) > 0 else f"There are no runs on {map_name}."