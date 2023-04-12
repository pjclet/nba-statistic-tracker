from check import *

def getStatLock(data, stat):

    line = 0
    over, under, tie = 0,0,0
    last = ()
    while True:
        over, under, tie = 0,0,0
        for i in range(len(data[stat])):
            if data[stat][i] >= line:
                over += 1
            elif data[stat][i] < line:
                under += 1
            else:
                tie += 1
        line += 0.5
        if over + under + tie:
            if over / (over + under + tie) >= 0.90:
                last = (over/(over + under + tie), over, under, tie)
            else:
                break
    
    return (line, last)

def printStatLock(stat, line, hit, depth, implied):
    print(f"{stat}: {line} \t {hit} / {depth} \t Implied odds: {round(implied * 100, 2)} %" )


def main():

    while True:
        name = getInput()
        depth = 50

        if name == "q": 
            quit()
        
        id = getPlayerId(name)

        if id == -404:
            continue

        playerData = getDataFrame(id)
        minutes = getMinuteData(playerData)

        newDataFrame = getDataFrame(id, minutes)

        print(f"\nShowing the most recent 10 games where {name.title()} played more than {minutes} minutes.\n")
        print(newDataFrame.head(10))
        print("\nShowing stats with -900 American odds (90% implied probability) ")
        print("\nLocks:")
        ptsLine = getStatLock(playerData.head(depth), 'PTS')
        rebLine = getStatLock(playerData.head(depth), 'REB')
        astLine = getStatLock(playerData.head(depth), 'AST')
        printStatLock("PTS", ptsLine[0], ptsLine[1][1], depth, ptsLine[1][0])
        printStatLock("REB", rebLine[0], rebLine[1][1], depth, rebLine[1][0])
        printStatLock("AST", astLine[0], astLine[1][1], depth, astLine[1][0])
        print(f"Total implied probability: {round((ptsLine[1][0] * rebLine[1][0] * astLine[1][0]) * 100, 2)} %\n" )



if __name__ == '__main__':
    main()