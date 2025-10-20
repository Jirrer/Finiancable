from Classes import Purchase
from MiscMethods import isDate
from pypdf import PdfReader
import re

# Issue - skipped netflix because it did not have a card number with it


def main():
    purchases = getPurchases(["testPdf"])
    categoriesDict = groupPurchases(purchases)

    print(categoriesDict)



def getPurchases(pdfsArray): 
    rawPurchases = parsePdf(pdfsArray)

    purchases = []
    for p in rawPurchases:
        purchases.append(categorisePurchase(p)) # < ready to start categorizing

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

    purchases = ''.join(pdfContent).split("\n")

    patterns = {"Fith/Third" : re.compile(r"\d{2}/\d{2}\s+\d+\.\d+.*?(?=X{12}\d{3}[X\d])")}
    
    foundPurchases = []
    for textContent in purchases:
        found = patterns["Fith/Third"].findall(textContent)

        for x in found: foundPurchases.append(x)

    return foundPurchases

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