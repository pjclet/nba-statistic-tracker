"""

- find minimum minutes using derivative
    - use this to remove any outlier games ()
    - this is to assume that the player is healthy 

- calculate average points again

- get player ID using their full name

- get future opponents?



"""

from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import players

# from oddsapi import OddsApiClient

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np



import requests

def getOdds():
    # An api key is emailed to you when you sign up to a plan
    API_KEY = '9b14f4e6cb8f01797776da76b32d7e17'

    SPORT = 'upcoming' # use the sport_key from the /sports endpoint below, or use 'upcoming' to see the next 8 games across all sports

    REGIONS = 'us' # uk | us | eu | au. Multiple can be specified if comma delimited

    MARKETS = 'h2h,spreads' # h2h | spreads | totals. Multiple can be specified if comma delimited

    ODDS_FORMAT = 'decimal' # decimal | american

    DATE_FORMAT = 'iso' # iso | unix

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    #
    # First get a list of in-season sports
    #   The sport 'key' from the response can be used to get odds in the next request
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    sports_response = requests.get('https://api.the-odds-api.com/v4/sports', params={
        'api_key': API_KEY
    })


    if sports_response.status_code != 200:
        print(f'Failed to get sports: status_code {sports_response.status_code}, response body {sports_response.text}')

    else:
        print('List of in season sports:', sports_response.json())



    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    #
    # Now get a list of live & upcoming games for the sport you want, along with odds for different bookmakers
    # This will deduct from the usage quota
    # The usage quota cost = [number of markets specified] x [number of regions specified]
    # For examples of usage quota costs, see https://the-odds-api.com/liveapi/guides/v4/#usage-quota-costs
    #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    odds_response = requests.get(f'https://api.the-odds-api.com/v4/sports/basketball_nba/odds', params={
        'api_key': API_KEY,
        'regions': REGIONS,
        'markets': MARKETS,
        'oddsFormat': ODDS_FORMAT,
        'dateFormat': DATE_FORMAT,
    })

    if odds_response.status_code != 200:
        print(f'Failed to get odds: status_code {odds_response.status_code}, response body {odds_response.text}')

    else:
        odds_json = odds_response.json()
        print('Number of events:', len(odds_json))
        print(odds_json)

        # Check the usage quota
        print('Remaining requests', odds_response.headers['x-requests-remaining'])
        print('Used requests', odds_response.headers['x-requests-used'])




# # player dictionary
# player_dict = players.get_players()

# from oddsapi import OddsAPI

# api_key = ''  # Replace with your API key
# odds_api = OddsApiClient(api_key)

# sport_key = 'basketball_nba'  # Specify the sport
# market = 'h2h'  # Specify the market

# lebron_name = 'LeBron James'
# lebron_odds = odds_api.get_odds(sport_key=sport_key, market=market, region='us', mappers={'h2h': 'moneyline'}, team=lebron_name)

# print(f"The current odds for {lebron_name} to score are {lebron_odds}")

# client = OddsApiClient(api_key='')
# response = client.retrieve_sports()

def getDataFrame(minute_filter = 0):
    # 203999 - luka, 2544 - lebron
    player_id = 2544  

    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=SeasonAll.all)

    # print(gamelog.get_data_frames()[0])

    last_10_games = gamelog.get_data_frames()[0].head(100)  # Get the last 10 games

    stats = last_10_games[['GAME_DATE', 'MATCHUP', 'WL', 'MIN' , 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT']]
    stats_new = stats[stats['MIN'] >= minute_filter]
    # stats.filter(stats)
    # stats = stats[stats.MIN >= 30]
    print(stats_new.head(10))
    return stats_new


def getTeamSchedule(team_name):
    # Get the team ID for the Lakers
    lakers = teams.find_teams_by_full_name(team_name)[0]
    lakers_id = lakers['id']

    # Use the leaguegamefinder endpoint to get the schedule for the Lakers
    gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=lakers_id)
    schedule = gamefinder.get_data_frames()[0]

    # Filter the schedule to show only future games
    future_games = schedule[schedule['GAME_DATE'] >= schedule['GAME_DATE'].max()]

    # print('*schedule')
    # print(schedule)
    # print(future_games)
    # print('*schedule\n')


def getMinuteData(stats):

    # print(lebron_stats)

    # pointsAverage = stats['PTS'].sum() / len(stats['PTS'])
    # print(pointsAverage)

    # print(stats)

    max_mins = max(stats['MIN'])

    x,minimum_mins,avg_mins = [],[],[]

    for i in range(max_mins):

        temp = []
        for j in range(len(stats)):
            
            # print(lebron_stats['MIN'][i])
            if stats['MIN'][j] == i:
                temp.append(stats['PTS'][j])
            
        if temp:
            # print(f"Minutes Played: {i}, Minimum points scored {min(temp)}, Average points score {sum(temp) / len(temp)}")
            x.append(i)
            minimum_mins.append(min(temp))
            avg_mins.append(sum(temp) / len(temp))
    
    derivative = []
    for i in range(1,len(x)):
        derivative.append((minimum_mins[i] - minimum_mins[i - 1]) / (x[i] - x[i - 1]))
    # print(derivative)
    # print(x)
    # print(minimum_mins)

    derivative_index = derivative.index(max(derivative[0:(len(derivative) // 4)]))
    # print(derivative_index)
    minute_cutoff = x[derivative_index]
    print(f"Calculated Minute Cutoff: {minute_cutoff}")
    return(minute_cutoff)
    
    




# plt.show()

def main():
    # # figure
    # fig = plt.figure()
    # ax = plt.axes()

    # dataframe viewing
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.width', 100)

    # calculate minute cutoff
    playerStats = getDataFrame()
    minutes = getMinuteData(playerStats)

    # getTeamSchedule('Los Angeles Lakers')

    newStats = getDataFrame(minutes)



    # ax.plot(x,minimum_mins)
    # ax.plot(x,avg_mins)



if __name__ == '__main__':
    main()