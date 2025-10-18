from Classes import Purchase

def main():
    purchases = getPurchases(["testPdf"])
    categoriesDict = groupPurchases(purchases)

    print(categoriesDict)



def getPurchases(pdfsArray): 
    rawPurchases = []
    for pdf in pdfsArray:
        rawPurchases.append(parsePdf(pdf))


    purchases = []
    for p in rawPurchases:
        purchases.append(categorisePurchase(p))

    return purchases
    

def parsePdf(input):
    return [(15.77, "MERCHANT PAYMENT WM SUPERCENTER # - 230022 1165 SUPERIOR DR SAINT JOHNS MI ON 081325FROM CARD#: XXXXXXXXXXXX677X"), 
            (24.00, "MERCHANT PAYMENT NNT HUCKLEBERRY - 006633 2900 N. HUBBARDSTON RD. PEWAMO MI ON 081525FROM CARD#: XXXXXXXXXXXX677X"),
            (48.00, "MERCHANT PAYMENT NNT HUCKLEBERRY - 006633 2900 N. HUBBARDSTON RD. PEWAMO MI ON 081525FROM CARD#: XXXXXXXXXXXX677X")
            ]

def categorisePurchase(input):
    return [Purchase(15.77, "shopping"), Purchase(24.00, "misc"), Purchase(48.00, "misc")]

def groupPurchases(inputArray):
    categories = {"food_drink": 0,
                  "gas": 0,
                  "housing": 0,
                  "shopping": 0,
                  "misc": 0}
    
    for purchase in inputArray[0]:
        categories[purchase.type] += purchase.value

    return categories


if __name__ == "__main__": main() 