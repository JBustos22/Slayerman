import re
import sys
import math
import time
import datetime
import requests

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_dateutil

from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import func, select, and_
from sqlalchemy.orm import sessionmaker

try:
    from settings import CONN_STRING
except:
    try:
        from src.settings import CONN_STRING
    except:
        print("WARNING: Could not import CONN_STRING from settings in mdd_scrape.py. Setting default value.")
        import keyring

        DB_PASSWORD = keyring.get_password('db_password', 'postgres')
        CONN_STRING = f"postgres://postgres:{DB_PASSWORD}@localhost:5432/Defrag"

# pylint: disable=E1101

sys.stdout.reconfigure(encoding='utf-8')

web_session = requests.Session()
web_session.headers.update({"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0"})

Q3_COLORS = {
    "red" : "^1",
    "green" : "^2",
    "yellow" : "^3",
    "blue" : "^4",
    "#4D87AB" : "^4",
    "turqoise" : "^5",
    "cyan" : "^5",
    "pink" : "^6",
    "purple" : "^6",
    "white" : "^7",
    "orange" : "^8",
    "grey" : "^9",
    "#B5B5B5" : "^9",
    "black" : "^0",
    "#5b5b5b" : "^0"
}

HOST = "https://q3df.org"


def convert_time_to_float(time_s: str):
    parts = time_s.split(":")

    try:
        minutes = int(parts[-3])
    except:
        minutes = 0

    seconds = int(parts[-2])
    mseconds = int(parts[-1])

    return float(minutes * 60 + seconds + mseconds / 1000)


def date_to_timestamp(date_s):
    # Horrible hack :^) *Technically not necessary
    date_s.replace("'", "20")

    a = parse_dateutil(date_s)

    return int(a.timestamp())


def spans_to_string(span):
    string = ""

    while True:
        if span == None:
            break

        # Extract color from span
        style = span["style"]
        color = re.search(r"color: (.+?)(;|$)", style).group(1)

        # Convert color to Q3 style
        if color in Q3_COLORS:
            color = Q3_COLORS[color]
        else:
            print("FOUND NEW COLOUR: " + color)

        # Extract partial string
        try:
            value = span.find("span").previousSibling
        except:
            value = span.text

        # Disregard unused color tags
        if value != None:
            string += color + value

        span = span.find("span")

    return string


def retry_web(method, args=[], retries=[10, 60, 600], valid_status_codes=[200]):
    for sleep_amount in retries:
        try:
            r = method(*args)
            if r.status_code not in valid_status_codes:
                raise Exception('Request in network_wrapper failed!')
            return r
        except Exception as e:
            print(e)
            time.sleep(sleep_amount)


def crawl_records():
    db_engine = create_engine(CONN_STRING, echo=False)
    Session = sessionmaker(bind=db_engine)

    meta_data = MetaData(bind=db_engine, reflect=True)
    mdd = meta_data.tables['mdd_records_ranked']

    db_session = Session()

    try:
        scraping = True
        has_changed = False
        page_counter = 1

        # Get latest timestamp in database
        query = select([func.max(mdd.c.timestamp)])
        max_ts = db_session.execute(query).first()[0]

        # Page scraping loop
        while scraping:
            # Get page
            page = retry_web(web_session.get, [HOST + f"/records?page={page_counter}"])
            page_soup = BeautifulSoup(page.text, "html.parser")

            # Get total number of records
            num_recs_s = page_soup.find("h3").text
            num_recs = int(re.search(r"Records \((.+?)\)", num_recs_s).group(1).replace(",", ""))

            # Get total number of pages
            num_pages = math.ceil(num_recs / 15)

            # Get table of records
            table = page_soup.find("table", {"class" : "recordlist"})

            for record in table.find_all("tr")[1:]: # Skip header row
                fields = record.find_all("td")

                # Pop returns last item in the list, so we are working bottom up
                server_s = spans_to_string(fields.pop().find("span", {"class" : "visname"}))

                # Remove color information :(
                server_s = re.sub(r"\^\d", "", server_s)

                physics_s = fields.pop().text.strip()
                rank_s = fields.pop().text.strip()
                map_s = fields.pop().text.strip()

                time_s = fields.pop().text.strip()
                time_seconds = convert_time_to_float(time_s)

                player = fields.pop()

                player_href = player.find("a", {"class" : "userlink"})["href"]
                player_id = int(re.search("id=(.+?)(&|$)", player_href).group(1))

                query = select([mdd.c.player_name, mdd.c.player_id]).where(mdd.c.player_id == player_id).limit(1)
                results = db_session.execute(query)


                if results.rowcount > 0:
                    player_name = results.first().player_name
                else:
                    # Get full player name from player page
                    player_page = retry_web(web_session.get, [HOST + player_href])
                    player_soup = BeautifulSoup(player_page.text, "html.parser")

                    player_name = spans_to_string(player_soup.find("span", {"class" : "visname"}))

                    # Remove color information :(
                    player_name = re.sub(r"\^\d", "", player_name)

                    time.sleep(1)

                country = player.find("img", {"class" : "flag"})["title"].upper()

                timestamp = datetime.datetime.fromtimestamp(date_to_timestamp(fields.pop().text))

                record = {"timestamp" : timestamp, "player_name" : player_name, "country" : country, "player_id" : player_id, "time" : time_s, "time_seconds" : time_seconds, "map_name" : map_s, "physics" : physics_s, "server_name" : server_s}

                if timestamp == max_ts:
                    # Check if this exact record already exists
                    # If so, skip it. If not, add it normally
                    query = select([func.count()]).where(and_(mdd.c.map_name == map_s, mdd.c.physics == physics_s, mdd.c.player_id == player_id, mdd.c.time_seconds == time_seconds)).limit(1)
                    results = db_session.execute(query)

                    if results.first()[0] > 0:
                        continue
                elif timestamp < max_ts:
                    # Stop scraping
                    scraping = False
                    break

                # Since we are introducing a new row to the database, we will have to
                # recalculate fields such as total_times
                has_changed = True

                # Check if this will overwrite an old record
                query = select([func.count()]).where(and_(mdd.c.map_name == map_s, mdd.c.physics == physics_s, mdd.c.player_id == player_id)).limit(1)
                results = db_session.execute(query)

                if results.first()[0] > 0:
                    # Update
                    query = mdd.update()\
                                .where(and_(mdd.c.map_name == map_s, mdd.c.physics == physics_s, mdd.c.player_id == player_id))\
                                .values(timestamp=timestamp, country=country, time=time_s, time_seconds=time_seconds, server_name=server_s)
                    db_session.execute(query)
                else:
                    # Insert
                    db_session.execute(mdd.insert(), record)

            # Check if we are on the final page
            if page_counter == num_pages:
                scraping = False
                break

            page_counter += 1

        if not has_changed:
            db_session.close()
            return

        # Calculate ancillary fields
        query = "UPDATE mdd_records_ranked m "\
                "SET "\
                    "total_times = sq1.total_times, "\
                    "player_pos = sq2.player_pos, "\
                    "percent_rank = (cast(sq1.total_times as float) - cast(sq2.player_pos - 1 as float) ) / cast(sq1.total_times as float), "\
                    "user_bestranks_rank = sq2.user_bestranks_rank, "\
                    "user_besttimes_rank = sq2.user_besttimes_rank "\
                "FROM "\
                    "( "\
                        "SELECT "\
                            "s.map_name, "\
                            "s.physics, "\
                            "COUNT(*) as total_times "\
                        "FROM "\
                            "mdd_records_ranked s "\
                        "GROUP BY "\
                            "s.map_name, "\
                            "s.physics "\
                    ") as sq1, "\
                    "( "\
                        "SELECT "\
                            "s.map_name, "\
                            "s.physics, "\
                            "s.player_id, "\
                            "RANK() OVER(PARTITION BY s.map_name, s.physics ORDER BY time_seconds) AS player_pos, "\
                            "ROW_NUMBER() OVER (PARTITION BY player_id, physics ORDER BY (CAST(total_times AS float) - CAST(player_pos - 1 AS float) ) / CAST(total_times AS float) DESC, total_times DESC) AS user_bestranks_rank, "\
                            "ROW_NUMBER() OVER (PARTITION BY player_id, physics ORDER BY (CAST(player_pos AS float) / CAST(total_times AS float)) ASC, total_times DESC) AS user_besttimes_rank "\
                        "FROM "\
                            "mdd_records_ranked s "\
                    ") as sq2 "\
                "WHERE "\
                    "sq1.map_name = m.map_name AND "\
                    "sq1.physics = m.physics AND "\
                    "sq2.map_name = m.map_name AND "\
                    "sq2.physics = m.physics AND "\
                    "sq2.player_id = m.player_id "
        db_session.execute(query)

        # Remake player stats table
        query = "DROP TABLE IF EXISTS mdd_player_stats; " \
                "CREATE TABLE mdd_player_stats AS SELECT * FROM mdd_player_stats_view;"
        db_session.execute(query)

        # # Remake country stats table. Uncomment when ready for use.
        # query = "DROP TABLE IF EXISTS mdd_country_stats; " \
        # "CREATE TABLE mdd_country_stats AS SELECT * FROM mdd_country_stats_view;"

        db_session.commit()
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()


def job():
    crawl_records()


if __name__ == "__main__":
    import schedule
    schedule.every(15).minutes.do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
