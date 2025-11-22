import ProccessingData

rawPurchases = ProccessingData.getRawPurchases([
    ("fifth_third", "C:\\Users\\jrirr\Downloads\\53Checkings.CSV"),
    ("truecc", "C:\\Users\\jrirr\Downloads\\TrueCC.csv")
    ])

for x in rawPurchases:
    print(x)