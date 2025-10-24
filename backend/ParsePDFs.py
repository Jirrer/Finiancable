import re, os, json
from Classes import Purchase
from MiscMethods import isDate, isFloat
from pypdf import PdfReader
from dotenv import load_dotenv

# Issue - skipped netflix because it did not have a card number with it
# To-Do: refactor

load_dotenv()

with open(os.getenv('DATA_LOCATION'), 'r', encoding='utf-8') as file:
    jsonData = json.load(file)

def main():
    lossDict = getLosses()

    print(lossDict)
    



def getLosses() -> dict:
    lossPDfS = [filePath for filePath in os.listdir(os.getenv('LOSS_PDF_LOCATION'))]

    rawLosses = pullLosses(lossPDfS)
    finalPurchases = categorisePurchases(rawPurchases)
    categoriesDict = groupPurchases(finalPurchases)

    return categoriesDict

def pullLosses(inputPDFs):
    pdfReadersArray = [PdfReader(f"{os.getenv('LOSS_PDF_LOCATION')}\\{pdf}") for pdf in inputPDFs]
    pdfContent = []

    for reader in pdfReadersArray:
        if reader.is_encrypted:
            reader.decrypt('') # <--- fix

        numPages = PdfReader.get_num_pages(reader)

        for index in range(numPages):
            page = reader.pages[index]

            pdfContent.append(page.extract_text())


    purchases = ''.join(pdfContent).split("\n")
    # <---- need to prepare text before to make sure no purchase allows more than one regex. ie - 5/3 can ONLY find 5/3

    losses = []

    for lossRegex in jsonData["lossess_regex"]:
        losses.append(
            (
                re.compile(lossRegex['regex']),
                lambda text: re.sub(
                    lossRegex['normalize'],
                    lossRegex['output'],
                    text
                )
            )
        )

    foundPurchases = [] 
    for textContent in purchases:
        for regex in losses:
            pattern, normalizer = regex

            cleanedText = normalizer(textContent)   

            found = pattern.findall(cleanedText)

            for match in found:
                foundPurchases.append(match)

    return foundPurchases

def categorisePurchases(purchasesArray):
    from LLM import RunLLM

    dates, values, messages = [], [], []

    for purchase in purchasesArray:
        dates.append(purchase[0])
        values.append(purchase[1])
        messages.append(purchase[2])

    if len(purchasesArray): categories = RunLLM(messages)

    output = [None] * len(purchasesArray)

    for index in range(len(purchasesArray)):
        output[index] = Purchase(values[index], categories[index], dates[index])

    return output

def groupPurchases(inputArray):
    categories = {}

    for category in jsonData["categories"]:
        categories[category] = 0.0
    
    for purchase in inputArray:
        categories[purchase.category] += float(purchase.value)

    return categories

if __name__ == "__main__": main() 