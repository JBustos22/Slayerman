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
    with open(f'admin/{json_f}.json', 'w') as outfile:
        json.dump(dict, outfile, indent=4)


def start_server(server):
    EC2 = boto3.client('ec2', region_name=server['region'])
    EC2.start_instances(InstanceIds=[server['instance_id']], DryRun=False)
    running = EC2.get_waiter('instance_running')
    running.wait()


def stop_server(server):
    EC2 = boto3.client('ec2', region_name=server['region'])
    EC2.stop_instances(InstanceIds=[server['instance_id']], DryRun=False)
    stopped = EC2.get_waiter('instance_stopped')
    stopped.wait()


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