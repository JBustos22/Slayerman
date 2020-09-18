from tabulate import tabulate
from settings import DB_PASSWORD, DB_HOST
from sqlalchemy import create_engine


def get_user_data(discord_id: str, df_map: str, physics: str= 'all'):
    db_string = f"postgres://postgres:{DB_PASSWORD}@{DB_HOST}:5432/Defrag"
    db = create_engine(db_string)

    with db.connect() as conn:
        # Read
        select_statement = "select player_pos, total_times, time, physics, timestamp " \
                           "from mdd_records_ranked mdd join discord_ids discord " \
                           "on mdd.player_id=discord.mdd_id " \
                           "where discord_id = %s " \
                           "and map_name=%s " + ("and physics=%s" if physics != "all" else '')
        replace_vars = (discord_id, df_map, physics) if physics != 'all' else (discord_id, df_map)
        result_set = conn.execute(select_statement, replace_vars)
        rows = list()
        for r in result_set:
            rank = f"{r.player_pos}/{r.total_times}"
            time = r.time
            physics = r.physics
            date = r.timestamp.strftime("%m/%d/%Y")
            rows.append([rank, time, physics, date])
        if len(rows) > 0:
            return f"```{tabulate(rows, headers=['Rank', 'Time', 'Physics', 'Date'])}```"
        else:
            return f"You have no such time(s) on this map"
