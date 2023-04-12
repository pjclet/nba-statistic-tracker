from check import *

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

        getStats(playerData.head(10), name.title())

        getLinearModel(playerData.head(50), 'PTS')
        getLinearModel(playerData.head(25), 'PTS')
        getLinearModel(playerData.head(10), 'PTS')

        

if __name__ == '__main__':
    main()