import json
from discord import Embed, Colour
import boto3


def create_server_embed(ip=None, metadata=None):
    title = f":flag_{metadata['flag']}: {metadata['location']}"
    url = f"https://pingtestlive.com/amazon-ping"
    thumbnail = metadata["thumbnail"]

    server_embed = Embed(title=title, url=url, color=Colour(0x9FC1E4))
    server_embed.set_thumbnail(url=thumbnail)
    # server_embed.set_author(name=author)

    # Add fields (embed subsections)
    server_embed.add_field(name=ip, value=f"`defrag://{metadata['flag']}.q3df.run`", inline=False)
    if metadata['status'] == "Stopped":
        status_emoji = ":red_circle:"
    elif metadata['status'] == "Active":
        status_emoji = ":green_circle:"
    elif metadata['status'] in ["Starting", "Stopping"]:
        status_emoji = ":orange_circle:"
    else:
        status_emoji = ":white:circle"

    server_embed.add_field(name=f"Status", value=f"{status_emoji} {metadata['status']}", inline=True)
    return server_embed


def update_json(json_f, dict):
    with open(f'servers/{json_f}.json', 'w') as outfile:
        json.dump(dict, outfile, indent=4)


def start_server(server):
    EC2 = boto3.client('ec2', region_name=server['region'])
    EC2.start_instances(InstanceIds=[server['instance_id']], DryRun=False)
    running = EC2.get_waiter('instance_running')
    running.wait(InstanceIds=[server['instance_id']])


def stop_server(server):
    EC2 = boto3.client('ec2', region_name=server['region'])
    EC2.stop_instances(InstanceIds=[server['instance_id']], DryRun=False)
    stopped = EC2.get_waiter('instance_stopped')
    stopped.wait(InstanceIds=[server['instance_id']])


def get_df_launcher_url(address, server_region):
    import urllib
    import requests
    key = 'f3e39987f57eda7e24ed7e62c5977d46967e6'
    url = urllib.parse.quote(f'defrag://{address}')
    name = f'df-{server_region.lower()}'
    r = requests.get('http://cutt.ly/api/api.php?key={}&short={}&name={}'.format(key, url, name))
    try:
        return json.loads(r.text)['url']['shortLink']
    except KeyError:
        return f"https://cutt.ly/df-{server_region.lower()}"


def scrape_servers_data():
    import requests
    from bs4 import BeautifulSoup
    from dateutil import parser
    """ Obtains data from q3df.org/servers using web scraping"""
    url = f'https://q3df.org/serverlist'
    r = requests.get(url, verify=False)
    soup = BeautifulSoup(r.text, 'html.parser')
    server_ids = [ele.get('id').split('_')[-1] for ele in soup.findAll('div', {'class': 'server-item shadow'})]
    server_names = [ele.text for ele in soup.findAll('div', {'class': 'server-head'})]
    server_states = [ele.find('ul').text.strip('\n').split('\n') for ele in soup.findAll('div', {'class': 'server-map-info'})]
    server_players_qty = [len(ele.find_all('span', {'class':'visname'})) for ele in soup.findAll('div', {'class': 'server-players'})]
    update_time_raw = soup.findAll('div', {'id': 'server-list'})[0].find('span').text.strip('(last update: ').strip(')')
    servers_data = {'update_time': parser.parse(update_time_raw)}
    for i in range(len(server_ids)):
        state = server_states[i]
        server_state = {
            "ip": state[0],
            "map_name": state[1],
            "physics": state[2]
        }
        server_details = {
            "name": server_names[i],
            "state": server_state,
            "players_qty": server_players_qty[i]
        }
        servers_data[server_ids[i]] = server_details

    return servers_data