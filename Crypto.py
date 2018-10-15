import requests
import os
import json
import sched, time


def load_exchange():
    #Open a text file where all the crypto currency pairs are stored -- LIQUI
    scriptpath = os.path.dirname(os.path.realpath('__file__'))
    filepath = os.path.join(scriptpath, "LiquiPairs.txt")

    pair_file = open(filepath, "r")

    Liquipairs = pair_file.readlines()
    Liquipairs = [x.strip('\n') for x in Liquipairs]


    #Same of Bittrix now
    filepath = os.path.join(scriptpath, "BittrixPairs.txt")

    pair_file = open(filepath, "r")

    BittrixPairs = pair_file.readlines()
    BittrixPairs = [x.strip('\n') for x in BittrixPairs]

    pair_file.close()


    #Now we start building our API calls
    baseURL_Liqui = 'https://api.liqui.io/api/3/depth/'
    baseURL_Bittrix = 'https://bittrex.com/api/v1.1/public/getorderbook?market='

    outpath = os.path.join(scriptpath, "Output.txt")
    outfile = open(outpath, 'w')


    #We have all the pairs, now go through each pair, make Liqui API calls, and process data
    for i in range(len(BittrixPairs)):
        
        rawpath1 = os.path.join(scriptpath, "Liqui - " + Liquipairs[i] + ".txt")
        rawpath2 = os.path.join(scriptpath, "Bittrix - " + BittrixPairs[i] + ".txt")
        
        flag1 = False
        flag2 = True
        
        #Liqui
        requestURL = baseURL_Liqui + Liquipairs[i] + '?limit=3'
        response = requests.get(requestURL)

        LiquiJSON = json.loads(response.text)

        for key in LiquiJSON:
            if Liquipairs[i] in key:
                flag1 = True
                with open(rawpath1, 'w') as rawfile:
                    json.dump(LiquiJSON, rawfile)
                rawfile.close()

        if flag1 == False:
            print 'Liquid Failed - ' + str(i)
        
        
        #Bittrix
        requestURL = baseURL_Bittrix + BittrixPairs[i] + '&type=both'
        response2 = requests.get(requestURL)

        BittrixJSON = json.loads(response2.text)
        
        if BittrixJSON['success'] == False:
            print 'Bittrix Failed - ' + str(i)
            flag2 = False

        else:
            with open(rawpath2, 'w') as rawfile:
                json.dump(BittrixJSON, rawfile)
            rawfile.close()


        #Perform calculations and output to output.txt
        if flag1 == True & flag2 == True:

            outfile.write(Liquipairs[i] + '\n')
            
            #Buy from Liqui, sell to Bittrix
            quantitiesSell = [LiquiJSON[Liquipairs[i]]["asks"][0][1], LiquiJSON[Liquipairs[i]]["asks"][1][1], LiquiJSON[Liquipairs[i]]["asks"][2][1]]
            quantitiesBuy = [BittrixJSON['result']['buy'][0]['Quantity'], BittrixJSON['result']['buy'][1]['Quantity'], BittrixJSON['result']['buy'][2]['Quantity']]

            for j in range(3):
                if LiquiJSON[Liquipairs[i]]["asks"][j][1] == max(quantitiesSell):
                    sellqty = LiquiJSON[Liquipairs[i]]["asks"][j][1]
                    sellrate = LiquiJSON[Liquipairs[i]]["asks"][j][0]
                    break

            for k in range(3):
                if BittrixJSON['result']['buy'][k]['Quantity'] == max(quantitiesBuy):
                    buyqty = BittrixJSON['result']['buy'][k]['Quantity']
                    buyrate = BittrixJSON['result']['buy'][k]['Rate']
                    break

            if sellqty > buyqty:
                outfile.write(str(buyrate * buyqty * 0.9975 - sellrate * buyqty * 0.9975) + '\n')

            else:
                outfile.write(str(buyrate * sellqty * 0.9975 - sellrate * sellqty * 0.9975) + '\n')


            #Buy from Bittrix, sell to Liqui
            quantitiesBuy2 = [LiquiJSON[Liquipairs[i]]["bids"][0][1], LiquiJSON[Liquipairs[i]]["bids"][1][1], LiquiJSON[Liquipairs[i]]["bids"][2][1]]
            quantitiesSell2 = [BittrixJSON['result']['sell'][0]['Quantity'], BittrixJSON['result']['sell'][1]['Quantity'], BittrixJSON['result']['sell'][2]['Quantity']]

            for l in range(3):
                if LiquiJSON[Liquipairs[i]]["bids"][l][1] == max(quantitiesBuy2):
                    buyqty2 = LiquiJSON[Liquipairs[i]]["bids"][l][1]
                    buyrate2 = LiquiJSON[Liquipairs[i]]["bids"][l][0]
                    break
            
            for m in range(3):
                if BittrixJSON['result']['sell'][m]['Quantity'] == max(quantitiesSell2):
                    sellqty2 = BittrixJSON['result']['sell'][m]['Quantity']
                    sellrate2 = BittrixJSON['result']['sell'][m]['Rate']
                    break

            if sellqty2 > buyqty2:
                outfile.write(str(buyrate2 * buyqty2 * 0.9975 - sellrate2 * buyqty2 * 0.9975) + '\n')

            else:
                outfile.write(str(buyrate2 * sellqty2 * 0.9975 - sellrate2 * sellqty2 * 0.9975) + '\n')


        else:
            outfile.write('Currency Pair: ' + Liquipairs[i] + ' API calls failed')

    outfile.close()


load_exchange()
