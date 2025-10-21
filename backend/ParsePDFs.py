from Classes import Purchase
from MiscMethods import isDate, isFloat
from pypdf import PdfReader
import re

# Issue - skipped netflix because it did not have a card number with it


def main(pdfs: list):
    purchases = getPurchases(pdfs)
    categoriesDict = groupPurchases(purchases)

 

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

    patterns = {"Fith/Third" : re.compile(r"(\d{2}/\d{2}\s+\d+\.\d+)(.*?)(?=X{12}\d{3}[X\d])")}
    
    foundPurchases = []
    for textContent in purchases: # <-- fix ai slop
        normilzedText = re.sub(patterns["Fith/Third"], r"\1 \2", textContent) # <-- fix ai slop

        found = patterns["Fith/Third"].findall(normilzedText) # <-- fix ai slop

        for match in found: # <-- fix ai slop
            full_purchase = f"{match[0]}{match[1]}" # <-- fix ai slop
            foundPurchases.append(full_purchase) # <-- fix ai slop


    return foundPurchases

def categorisePurchase(textInput):
    date, value, message = None, None, []

    for word in textInput.split(' '):
        if isDate(word): date = word
        elif isFloat(word): value = word
        else: message.append(word)

    return Purchase(value, getPurchaseType(' '.join(message)), date)

def getPurchaseType(message: str):
    # <-- needs to figure out what type of purchase it is

    print(message)

    return 'misc'

def groupPurchases(inputArray):
    categories = {"food_drink": 0.0,
                  "gas": 0.0,
                  "housing": 0.0,
                  "shopping": 0.0,
                  'subscriptions': 0.0,
                  "misc": 0.0}
    
    for purchase in inputArray:
        categories[purchase.type] += float(purchase.value)

    return categories

if __name__ == "__main__": main() 