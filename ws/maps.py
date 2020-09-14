import requests
from bs4 import BeautifulSoup
import math as m
from random import randint


def get_random_map():
    maps_per_page = 50
    num_maps = 11251 # hard coded for speed
    max_page = m.ceil(num_maps/maps_per_page)
    page_num = randint(1, max_page)
    entry_num = randint(1, maps_per_page)

    # Scrape random entry at random page
    url = f"http://ws.q3df.org/maps/?map=&fo=2&mo=1&auf=2&show=50&page={page_num}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    entry = soup.find('table', attrs={'id': 'maps_table'}).find_all('tr')[entry_num]
    map_name = entry.find_all('td')[2].text.strip('\n')

    return map_name


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
