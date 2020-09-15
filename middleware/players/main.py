
def format_player_flags(players, countries):
    country_players = []
    for i in range(0, len(players)):
        country_players.append(f"{countries[i]}` |{players[i]}")
    return country_players
