"""

- find minimum minutes using derivative
    - use this to remove any outlier games ()
    - this is to assume that the player is healthy 

- calculate average points again [X]

- get player ID using their full name [X]

- get future opponents?

Dependencies:
pip3 install nba_api
pip3 install pandas

"""

from nba_api.stats.endpoints import playergamelog
from nba_api.stats.library.parameters import SeasonAll
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.static import players

import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np




def getDataFrame(player_id, minute_filter = 0):

    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=SeasonAll.all)

    # print(gamelog.get_data_frames()[0])

    last_10_games = gamelog.get_data_frames()[0].head(100)  # Get the last 10 games

    stats = last_10_games[['GAME_DATE', 'MATCHUP', 'WL', 'MIN' , 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FG_PCT', 'FG3_PCT', 'FT_PCT']]
    stats_new = stats[stats['MIN'] >= minute_filter]
    # stats.filter(stats)
    # stats = stats[stats.MIN >= 30]
    # print(stats_new.head(10))
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
    
def getStats(data, name):
    
    pointsAverage = data['PTS'].sum() / len(data['PTS'])
    reboundsAverage = data['REB'].sum() / len(data['REB'])
    assistsAverage = data['AST'].sum() / len(data['AST'])

    print(f"\nIn the past {len(data)} games, {name} has averaged the following:\n" + \
          f"Points: \t{pointsAverage}\nRebounds: \t{reboundsAverage}\nAssists: \t{assistsAverage}")

def checkLine(data, stat, line):

    over, under = 0,0
    for i in range(len(data[stat])):
        if data[stat][i] > line:
            over += 1
        elif data[stat][i] < line:
            under += 1
    
    print(f"Line (past {len(data)} games): {stat} @ {line} - Over: {over} / Under: {under}")





# plt.show()

def getPlayerId(input):

    player_dict = players.get_players()
    input = input

    for i in range(len(player_dict)):
        if player_dict[i]['full_name'].lower() == input or\
                player_dict[i]['first_name'].lower() == input or\
                player_dict[i]['last_name'].lower() == input:
            
            print(f"\nID for {player_dict[i]['full_name']} found: {player_dict[i]['id']}")
            return player_dict[i]['id']
            
    
    print("ERROR: Player not found in database.")
    quit()

def getInput():
    return input("Name of Player (q to quit): \n").strip().lower()

def main():
    # # figure
    # fig = plt.figure()
    # ax = plt.axes()



    # dataframe viewing
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.max_columns', 12)
    pd.set_option('display.width', 100)

    while True:
        # get player
        name = getInput()

        if name == "q": 
            quit()

        id = getPlayerId(name)

        # calculate minute cutoff
        playerData = getDataFrame(id)
        minutes = getMinuteData(playerData)

        newDataFrame = getDataFrame(id, minutes)

        print(f"\nShowing the most recent 10 games where {name.title()} played more than {minutes} minutes.\n")
        print(newDataFrame.head(10))
        
        # base stats off of last 50 and 10 games
        getStats(playerData.head(50), name.title())

        getStats(playerData.head(10), name.title())

        command = ""

        while True:
            print("\nOptions:\t- Points Line (p)\t- Rebounds Line (r)\t- Assists (a)\t- New Player (n)\t- Quit (q)")
            command = input("Enter command: ").strip().lower()
            
            # exit or error conditions
            if command == "q":
                quit()
            if command == "n":
                break
            if not command in ["p","r","a"]:
                print("ERROR: Invalid command.")
                continue

            number = input("Enter stat number (e.g. Points over/under 20.5, assists over 4.5, etc.): ").strip()
            if number.isalpha():
                print("ERROR: Please enter an integer or float.")
                continue

            if command == "p":
                checkLine(playerData, 'PTS', float(number))
                checkLine(playerData.head(50), 'PTS', float(number))
                checkLine(playerData.head(10), 'PTS', float(number))
            elif command == "r":
                checkLine(playerData, 'REB', float(number))
                checkLine(playerData.head(50), 'REB', float(number))
                checkLine(playerData.head(10), 'REB', float(number))
            elif command == "a":
                checkLine(playerData, 'AST', float(number))
                checkLine(playerData.head(50), 'AST', float(number))
                checkLine(playerData.head(10), 'AST', float(number))
        
        


    # getOdds()

    # ax.plot(x,minimum_mins)
    # ax.plot(x,avg_mins)



if __name__ == '__main__':
    main()