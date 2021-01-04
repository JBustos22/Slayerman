from settings import db


def set_id(discord_id, mdd_id):
    if validate_mdd_id(mdd_id):
        with db.connect() as conn:
            select_statement = f"INSERT INTO discord_ids (discord_id, mdd_id) " \
                               f"VALUES (%s, %s) " \
                               f"ON CONFLICT (discord_id) DO UPDATE " \
                               f"SET discord_id = excluded.discord_id, mdd_id = excluded.mdd_id;"
            replace_vars = (discord_id, mdd_id)
            conn.execute(select_statement, replace_vars)
            return None
    else:
        return f"No profile with id {mdd_id} exists in the mdd rankings."


def get_id(discord_user):
    discord_id = str(discord_user.id)
    with db.connect() as conn:
        select_statement = f"SELECT mdd_id FROM discord_ids WHERE discord_id=%s"
        replace_vars = (discord_id,)
        result_set = conn.execute(select_statement, replace_vars)
        if result_set.rowcount == 1:
            for row in result_set:
                return f"{discord_user.display_name}, your mdd id is set to {row.mdd_id}." \
                       f" To set your mdd id, use !myid <mdd_id>"
        else:
            return f"{discord_user.display_name}, you do not have an mdd id tied to your account." \
                   f" To set your mdd id, use !myid <mdd_id>"


def validate_mdd_id(mdd_id):
    with db.connect() as conn:
        select_statement = "SELECT count(1) > 0 FROM mdd_player_stats WHERE player_id = %s"
        replace_vars = (mdd_id)
        result = conn.execute(select_statement, replace_vars)
        return result.first()[0]
