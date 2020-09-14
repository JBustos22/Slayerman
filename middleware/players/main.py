
def attach_country_to_players(players, countries):
    country_players = []
    for i in range(0, len(players)):
        country_players.append(f"{countries[i]} {players[i]}")
    return country_players