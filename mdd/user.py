from tabulate import tabulate
from settings import CONN_STRING
from sqlalchemy import create_engine


def get_user_times(discord_id: str, df_map: str, physics: str= 'all'):
    db = create_engine(CONN_STRING)

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


def get_overall_user_stats(discord_id, physics=None):
    db = create_engine(CONN_STRING)
    with db.connect() as conn:
        # Read
        select_statement = "SELECT \
                            country \
                            ,player_id \
                            ,player_name \
                            ,SUM(total_times) as total_times \
                            ,SUM(total_time_seconds) as total_time_logged \
                            ,SUM(total_world_recs) as total_world_records \
                            ,SUM(total_top3_recs) as total_top_3_times \
                            ,SUM(total_top10_recs) as total_top_10_times \
                            FROM mdd_player_stats m JOIN discord_ids d ON m.player_id=d.mdd_id \
                            WHERE discord_id=%s \
                            GROUP BY country, player_id, player_name"
        replace_vars = (discord_id,)
        result_set = conn.execute(select_statement, replace_vars)
        if result_set.rowcount == 1:
            for row in result_set:
                stats_dict = dict(row)
                # total seconds to human-readable
                total_time = stats_dict['total_time_logged']
                day = int(total_time // (24 * 3600))
                total_time = total_time % (24 * 3600)
                hour = int(total_time // 3600)
                total_time %= 3600
                minutes = int(total_time // 60)
                total_time %= 60
                seconds = int(total_time)
                stats_dict['total_time_logged'] = f"{day} days, {hour} hours, {minutes} minutes, and {seconds} seconds"

                # percentage calculations
                total_times, top1, top3, top10 = [stats_dict[datum] for datum in ['total_times', 'total_world_records',
                                                               'total_top_3_times', 'total_top_10_times']]
                stats_dict['total_world_records'] = f"{top1} ({round(top1/total_times * 100, 2)}%)"
                stats_dict['total_top_3_times'] = f"{top3} ({round(top3 / total_times * 100, 2)}%)"
                stats_dict['total_top_10_times'] = f"{top10} ({round(top10 / total_times * 100, 2)}%)"
                return stats_dict
        raise Exception("No stats available.")