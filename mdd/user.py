from tabulate import tabulate
from settings import DB_PASSWORD
from sqlalchemy import create_engine


def get_user_data(discord_id: str, df_map: str, physics: str):
    db_string = f"postgres://postgres:{DB_PASSWORD}@localhost:5432/Defrag"
    db = create_engine(db_string)

    with db.connect() as conn:
        # Read
        select_statement = "select player_pos, ttl_times, run_tm, phys_cd, run_tmstp " \
                           "from mdd_records_ranked mdd join discord_ids discord " \
                           "on mdd. player_id=discord.mdd_id " \
                           "where discord_id = %s " \
                           "and map_nm=%s " \
                           "and phys_cd in (%s)"
        result_set = conn.execute(select_statement,(discord_id, df_map, physics+"-run"))
        rows = list()
        for r in result_set:
            rank = f"{r.player_pos}/{r.ttl_times}"
            time = r.run_tm
            physics = r.phys_cd
            date = r.run_tmstp.strftime("%m/%d/%Y")
            rows.append([rank, time, physics, date])
        if len(rows) > 0:
            return f"```{tabulate(rows, headers=['Rank', 'Time', 'Physics', 'Date'])}```"
        else:
            return f"You have no{'' if physics=='run' else ' ' + physics} time on this map"
