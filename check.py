"""

- find minimum minutes using derivative [X]
    - use this to remove any outlier games ()
    - this is to assume that the player is healthy 

- calculate average points again [X]

- get player ID using their full name [X]

- get future opponents?

- linear regression model

- add records against certain team

- ML algorithm?

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
from sklearn.linear_model import LinearRegression

# linear regression model
def getLinearModel(data, stat):
    X = list([x] for x in range(0,len(data)))
    Y = data[stat].values.reshape(-1, 1)
    # print(X, Y)
    linear_regressor = LinearRegression()  # create object for the class
    linear_regressor.fit(X, Y)  # perform linear regression
    Y_pred = linear_regressor.predict(X)  # make predictions
    
    # print(Y_pred[0])
    return round(Y_pred[0][0], 2)


# get online data using nba_api given the nba player id
def getDataFrame(player_id, minute_filter = 0):

    gamelog = playergamelog.PlayerGameLog(player_id=player_id, season=SeasonAll.all)
    

    last_10_games = gamelog.get_data_frames()[0].head(100)  # Get the last 10 games

    stats = last_10_games[['GAME_DATE', 'MATCHUP', 'WL', 'MIN' , 'PTS', 'REB', 'AST', 'STL', 'BLK', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT']]
    stats_new = stats[stats['MIN'] >= minute_filter]

    return stats_new

# return the minimum minutes to remove skewed data
def getMinuteData(stats):

    max_mins = max(stats['MIN'])

    x,minimum_mins,avg_mins = [],[],[]

    for i in range(max_mins):

        temp = []
        for j in range(len(stats)):
            
            if stats['MIN'][j] == i:
                temp.append(stats['PTS'][j])
            
        if temp:
            x.append(i)
            minimum_mins.append(min(temp))
            avg_mins.append(sum(temp) / len(temp))
    
    derivative = []
    for i in range(1,len(x)):
        derivative.append((minimum_mins[i] - minimum_mins[i - 1]) / (x[i] - x[i - 1]))

    # check the first 1/4 of the data and cutoff the data with the highest derivative (largest change)
    derivative_index = derivative.index(max(derivative[0:(len(derivative) // 4)]))
    minute_cutoff = x[derivative_index]

    print(f"Calculated Minute Cutoff: {minute_cutoff}")

    return(minute_cutoff)
    
# get the main 3 stat averages
def getStats(data, name):
    
    pointsAverage = data['PTS'].sum() / len(data['PTS'])
    reboundsAverage = data['REB'].sum() / len(data['REB'])
    assistsAverage = data['AST'].sum() / len(data['AST'])
    threeAverage = data['FG3M'].sum() / len(data['FG3M'])
    praAverage = round(sum([pointsAverage, reboundsAverage, assistsAverage]),2)

    pointsPrediction = getLinearModel(data, 'PTS')
    reboundsPrediction = getLinearModel(data, 'REB')
    assistPrediction = getLinearModel(data, 'AST')

    print(f"\nIn the past {len(data)} games, {name} has averaged the following:\n" + \
          f"Points: \t{pointsAverage}\t-\tProjected Points: \t{pointsPrediction}\nRebounds: \t{reboundsAverage}\t-\tProjected Rebounds: \t{reboundsPrediction}\nAssists: \t{assistsAverage}\t-\tProjected Assists: \t{assistPrediction}\nThrees: \t{threeAverage}\nPRA: \t\t{praAverage}")

# count how many times the line was over and how many times it was under
def checkLine(data, stat, line):

    over, under = 0,0
    for i in range(len(data[stat])):
        if data[stat][i] > line:
            over += 1
        elif data[stat][i] < line:
            under += 1
    
    overOdds, underOdds = int,int
    
    if over > under:
        decimal = 1/(over / (over + under))
        if under:
            underOdds = "+" + str(int((1/(under/over)) * 100))
            overOdds = int((-100) // (decimal - 1))
        else:
            underOdds = "+999999999"
            overOdds = "-∞"
        
    elif over < under:
        decimal = 1/(under / (over + under))
        if over:
            overOdds = "+" + str(int((1/(over/under)) * 100))
            underOdds = int((-100) // (decimal - 1))
        else:
            overOdds = "+999999999"
            underOdds = "-∞"
        
    else:
        underOdds = overOdds = "-100"

    print(f"Line (past {len(data)} games):\t{stat} @ {line} - Over: {over} ({overOdds}) / Under: {under} ({underOdds})")

# get the player id from the player dictionary given a first name, last name, or full name
def getPlayerId(input):

    player_dict = players.get_players()
    input = input

    for i in range(len(player_dict)):
        if player_dict[i]['full_name'].lower() == input or\
                player_dict[i]['first_name'].lower() == input or\
                player_dict[i]['last_name'].lower() == input:
            
            print(f"\nNBA ID for {player_dict[i]['full_name']} found: {player_dict[i]['id']}")
            return player_dict[i]['id']
            
    print("ERROR: Player not found in database.")
    return -404

def getInput():
    return input("Name of Player (first, last or full) (q to quit)\n   >>> ").strip().lower()

def main():

    # dataframe viewing
    pd.set_option('display.max_rows', 10)
    pd.set_option('display.max_columns', 27)
    pd.set_option('display.width', 200)

    while True:
        # get player
        name = getInput()

        if name == "q": 
            quit()

        id = getPlayerId(name)

        if id == -404:
            continue

        # calculate minute cutoff
        playerData = getDataFrame(id)
        minutes = getMinuteData(playerData)

        newDataFrame = getDataFrame(id, minutes)

        print(f"\nShowing the most recent 10 games where {name.title()} played more than {minutes} minutes.\n")
        print(newDataFrame.head(10))
        
        # base stats off of last 50 and 10 games
        getStats(playerData.head(50), name.title())
        getStats(playerData.head(25), name.title())
        getStats(playerData.head(10), name.title())

        command = ""

        while True:
            print("\nOptions: Points (p), Rebounds (r), Assists (a), New Player (n), Quit (q)")
            command = input("   >>> ").strip().lower()
            
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
                checkLine(playerData.head(25), 'PTS', float(number))
                checkLine(playerData.head(10), 'PTS', float(number))
            elif command == "r":
                checkLine(playerData, 'REB', float(number))
                checkLine(playerData.head(50), 'REB', float(number))
                checkLine(playerData.head(25), 'REB', float(number))
                checkLine(playerData.head(10), 'REB', float(number))
            elif command == "a":
                checkLine(playerData, 'AST', float(number))
                checkLine(playerData.head(50), 'AST', float(number))
                checkLine(playerData.head(25), 'AST', float(number))
                checkLine(playerData.head(10), 'AST', float(number))

if __name__ == '__main__':
    main()