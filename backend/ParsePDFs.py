from Classes import Purchase
from MiscMethods import isDate
from pypdf import PdfReader

PaymentDefinitionConfidence = 1.0

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
    

def parsePdf(inputPDFs):
    pdfReadersArray = [PdfReader(pdf) for pdf in inputPDFs]
    pdfContent = []

    for reader in pdfReadersArray:
        if reader.is_encrypted:
            reader.decrypt('') # <--- fix

        numPages = PdfReader.get_num_pages(reader)

        for index in range(numPages):
            page = reader.pages[index]

            pdfContent.append(page.extract_text())

    purchases = pullPurchases(''.join(pdfContent))


    for x in purchases:
        print(f'{x}\n\n')



def pullPurchases(text: str) -> list:
    textArray = text.split("\n")

    foundPurchases = [content for content in textArray if isPurchase(content)]


    return foundPurchases

def isPurchase(content: str) -> bool:
    confidence = 0.0
    keyWords = {'transaction', 'debit', 'withdrawal', 'withdrawals/debits', 'withdrawals/debits-continueddate', 'payments'} # <-- make non static (move to json)

    for word in content.split(" "):
        if word.lower() in keyWords: confidence += 10.0
        if isDate(word): confidence += 5.0

    return confidence >= PaymentDefinitionConfidence



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