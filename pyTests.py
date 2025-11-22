import ProccessingData

def TEST_getRawPurchases():
    rawPurchases = ProccessingData.getRawPurchases([
        ("fifth_third", "C:\\Users\\jrirr\Downloads\\53Checkings.CSV"),
        ("truecc", "C:\\Users\\jrirr\Downloads\\TrueCC.csv")
        ])
    
    return rawPurchases

def TEST_categorizePurchases():
    return ProccessingData.categorizePurchases(TEST_getRawPurchases())

def printPurchases(purchasesInput: list) -> None:
    for purchase in purchasesInput:
        print(f"Value: {purchase.value}, Category: {purchase.category}, Date: {purchase.date}, Info: {purchase.info}")


if __name__ == "__main__":
    # TEST_getRawPurchases()
    # TEST_categorizePurchases()

    printPurchases(TEST_categorizePurchases())