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
        result_set.close()
        if len(rows) > 0:
            return f"```{tabulate(rows, headers=['Rank', 'Time', 'Physics', 'Date'])}```"
        else:
            return f"You have no such time(s) on this map"


def get_overall_user_stats(discord_id=None, mdd_id=None):
    db = create_engine(CONN_STRING)
    if discord_id is not None:
        from_where = "FROM mdd_player_stats m JOIN discord_ids d ON m.player_id=d.mdd_id WHERE discord_id=%s"
        replace_vars = (discord_id,)
    else:
        from_where = "FROM mdd_player_stats WHERE player_id=%s"
        replace_vars = (mdd_id,)
    with db.connect() as conn:
        # Read
        select_statement = f"SELECT \
                            country \
                            ,player_id \
                            ,player_name \
                            ,SUM(total_times) as total_times \
                            ,SUM(total_time_seconds) as total_time_logged \
                            ,SUM(total_world_recs) as total_world_records \
                            ,SUM(total_top3_recs) as total_top_3_times \
                            ,SUM(total_top10_recs) as total_top_10_times \
                            {from_where} \
                            GROUP BY country, player_id, player_name"
        result_set = conn.execute(select_statement, replace_vars)
        if result_set.rowcount == 1:
            for row in result_set:
                stats_dict = dict(row)
                # total seconds to human-readable
                total_time = stats_dict['total_time_logged']
                days, hours, minutes, secs = process_total_seconds_to_readable(total_time)
                stats_dict['total_time_logged'] = f"{days} days, {hours} hours, {minutes} minutes, and {secs} seconds"

                # percentage calculations
                total_times, top1, top3, top10 = [stats_dict[datum] for datum in ['total_times', 'total_world_records',
                                                               'total_top_3_times', 'total_top_10_times']]
                stats_dict['total_world_records'] = f"{top1} ({round(top1/total_times * 100, 2)}%)"
                stats_dict['total_top_3_times'] = f"{top3} ({round(top3 / total_times * 100, 2)}%)"
                stats_dict['total_top_10_times'] = f"{top10} ({round(top10 / total_times * 100, 2)}%)"
            result_set.close()
            return stats_dict
        raise Exception("No statistics found.")


def get_physics_user_stats(physics_string, discord_id=None, mdd_id=None):
    db = create_engine(CONN_STRING)
    supported_physics = {
        'vq3' : 'vq3-run',
        'vq3.1' : 'vq3-ctf1',
        'vq3.2' : 'vq3-ctf2',
        'vq3.3' : 'vq3-ctf3',
        'vq3.4' : 'vq3-ctf4',
        'vq3.5': 'vq3-ctf5',
        'vq3.6': 'vq3-ctf6',
        'vq3.7': 'vq3-ctf7',
        'cpm': 'cpm-run',
        'cpm.1': 'cpm-ctf1',
        'cpm.2': 'cpm-ctf2',
        'cpm.3': 'cpm-ctf3',
        'cpm.4': 'cpm-ctf4',
        'cpm.5': 'cpm-ctf5',
        'cpm.6': 'cpm-ctf6',
        'cpm.7': 'cpm-ctf7',
    }
    if physics_string in supported_physics:
        physics = supported_physics[physics_string]
    else:
        raise Exception("Invalid physics.")

    with db.connect() as conn:
        # Read
        if discord_id is not None:
            from_where = "FROM mdd_player_stats m JOIN discord_ids d ON m.player_id=d.mdd_id " \
                         "WHERE discord_id=%s AND physics=%s"
            replace_vars = (discord_id, physics)
        else:
            from_where = "FROM mdd_player_stats WHERE player_id=%s AND physics=%s"
            replace_vars = (mdd_id, physics)

        select_statement = f"SELECT country \
                           ,player_id \
                           ,player_name \
                           ,physics \
                           ,total_times \
                           ,total_time_seconds as total_time_logged \
                           ,avg_pct_rank as average_percent_rank \
                           ,overall_pct_rank as overall_percent_rank \
                           ,total_world_recs as world_records \
                           ,world_recs_pct as top1_percent \
                           ,total_top3_recs as top_3_times \
                           ,top3_recs_pct as top3_percent \
                           ,total_top10_recs as top_10_times \
                           ,top10_recs_pct as top10_percent \
                           {from_where}"
        result_set = conn.execute(select_statement, replace_vars)
        if result_set.rowcount == 1:
            for row in result_set:
                stats_dict = dict(row)
                # total seconds to human-readable
                total_time = stats_dict['total_time_logged']
                days, hours, minutes, secs = process_total_seconds_to_readable(total_time)
                stats_dict['total_time_logged'] = f"{days} days, {hours} hours, {minutes} minutes, and {secs} seconds"
                total_times, top1, top3, top10 = [stats_dict[datum] for datum in ['total_times', 'world_records',
                                                                                  'top_3_times', 'top_10_times']]
                total_pc, top1_pc, top3_pc, top10_pc = [stats_dict.pop(datum) for datum in ['overall_percent_rank',
                                                                                            'top1_percent',
                                                                                            'top3_percent',
                                                                                            'top10_percent']]
                stats_dict['average_percent_rank'] = round(stats_dict['average_percent_rank'] * 100, 2)
                stats_dict['total_times'] = f"{total_times} ({round(total_pc * 100, 2)}%)"
                stats_dict['world_records'] = f"{top1} ({round(top1_pc * 100, 2)}%)"
                stats_dict['top_3_times'] = f"{top3} ({round(top3_pc * 100, 2)}%)"
                stats_dict['top_10_times'] = f"{top10} ({round(top10_pc * 100, 2)}%)"
            result_set.close()
            return stats_dict
        result_set.close()
        raise Exception("No statistics found.")


def process_total_seconds_to_readable(total_time):
    day = int(total_time // (24 * 3600))
    total_time = total_time % (24 * 3600)
    hour = int(total_time // 3600)
    total_time %= 3600
    minutes = int(total_time // 60)
    total_time %= 60
    seconds = int(total_time)
    return day, hour, minutes, seconds
