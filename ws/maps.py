import requests
from bs4 import BeautifulSoup
import math as m
from random import randint
from discord import Embed, Colour

def get_random_map():
    maps_per_page = 50
    # url = f"http://ws.q3df.org/maps/" \
    #     f"?map=&fo=2&cat=0&mo=1&ty=-1&df=-1&we=-1&it=-1&fc=-1&au=&auf=2&show={maps_per_page}&view=0"
    # r = requests.get(url)
    # soup = BeautifulSoup(r.text, 'html.parser')
    # result = soup.find('span', attrs={'id': 'resulttext'})
    # num_maps = int(result.text.split(' ')[2])
    num_maps = 11251 # hard coded for speed
    max_page = m.ceil(num_maps/maps_per_page)
    page_num = randint(1, max_page)
    entry_num = randint(1, maps_per_page)
    url = f"http://ws.q3df.org/maps/?map=&fo=2&mo=1&auf=2&show=50&page={page_num}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    entry = soup.find('table', attrs={'id': 'maps_table'}).find_all('tr')[entry_num]
    map_name = entry.find_all('td')[2].text.strip('\n')

    return map_name

def get_map_details(map_name):
    url = f"http://ws.q3df.org/map/{map_name}/"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    levelshot_url = 'https://ws.q3df.org'\
                            + soup.find('img', attrs={'id': 'mapdetails_levelshot'}).attrs['srcset']
    map_data = scrape_map_data(soup)
    map_embed = Embed(title=map_name, url=url, color=Colour(0xffffff))
    map_embed.set_image(url=levelshot_url)
    thumbnail_url = "https://ws.q3df.org/images/icons/32x32/defrag.png"
    map_embed.set_thumbnail(url=thumbnail_url)
    map_embed.set_author(name="Worldspawn Archive")
    for key, value in map_data.items():
        inline = False if key in ['Author', 'Description', 'Release Date'] else True
        map_embed.add_field(name=key, value=value, inline=inline)
    return map_embed


def scrape_map_data(map_soup):
    map_data = dict()
    map_data_table = map_soup.find("table", {"id": "mapdetails_data_table"})
    map_data['Description'] = map_data_table.find("td", string="Mapname").next_sibling.text
    map_data['Author'] = map_data_table.find("td", string="Author").parent.find("a").text
    map_data['Release Date'] = map_data_table.find("td", string="Release date").next_sibling.text
    physics = [field.text for field in map_data_table.find("td", string="Defrag physics").parent.find_all("a")]
    map_data['Physics'] = ', '.join(physics)

    # Optional fields:
    opt = ["Weapons", "Items", "Functions"]

    for key in opt:
        try:
            data_list = [img["title"] for img in map_data_table.find("td", string=key).parent.find_all("img")]
            data_string = ', '.join(data_list)
            map_data[key] = data_string
        except:
            pass
    return map_data
