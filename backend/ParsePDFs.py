from Classes import Purchase
from MiscMethods import isDate, isFloat
from pypdf import PdfReader
import re


# Issue - skipped netflix because it did not have a card number with it


def main(pdfs: list):
    purchases = getPurchases(pdfs)
    categoriesDict = groupPurchases(purchases)

    # print(purchases)
    # print(categoriesDict)

    # for x in purchases:
    #     print(x.category)

def getPurchases(pdfsArray: list): 
    rawPurchases = parsePdf(pdfsArray)

    return categorisePurchases(rawPurchases)

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
    # <---- need to prepare text before to make sure no purchase allows more than one regex. ie - 5/3 can ONLY find 5/3

    losses = [ # <-- explore different data types for storage
        (
            re.compile(r"(\d{2}/\d{2}\s+\d+\.\d+)(.*?)(?=\s?FROM\s?CARD#:\s?X{12}\d{3}[X\d])"),
            lambda text: re.sub(
                r"(\d{2}/\d{2}\s+\d+\.\d+)(.*?)(?=\s?FROM\s?CARD#:\s?X{12}\d{3}[X\d])",
                lambda m: f"{m.group(1)} {''.join(c for c in m.group(2) if not c.isdigit())}",
                text
            )
        ),

        (
            # re.compile(r"(\d\d/\d\d\s+\d+\.\d\d\s+.*?)(?=:?\s?TRUE ACH CO)"),
            re.compile(r"\d\d/\d\d"),
            lambda text: re.sub(
                # r"(\d\d/\d\d)(/\d\d)\s+(\d+\.\d\d)\s+(\d+\.\d\d)\s+(-\d+\.\d\d)\s+(.*?)(?=:?\s?TRUE ACH CO)",
                r"\d\d/\d\d/\d\d",
                # lambda m: f"{m.group(1)}99 {m.group(4)} {''.join(c for c in m.group(5) if not c.isdigit())}",
                r"\d\d/\d\d",
                text
            )
        )

    ]



    foundPurchases = [] 
    for textContent in purchases:
        for regex in losses:
            pattern, normalizer = regex

            cleanedText = normalizer(textContent)   

            found = pattern.findall(cleanedText)

            if len(found) == 1: found = [(found[0],)]


            for match in found:
                foundPurchases.append(''.join(match))

 
    # for x in foundPurchases:
    #     print(x)
    print(purchases)
    print(foundPurchases[0])

    return []

    return foundPurchases

def categorisePurchases(purchasesArray):
    from LLM import RunLLM

    dates, values, messages = [], [], []

    for purchase in purchasesArray:
        # print(purchase)
        currDate, currValue, currMessage, = None, None, []

        for word in purchase.split(' '):
            if isDate(word): currDate = word
            elif isFloat(word): currValue= word
            else: currMessage.append(word)

        dates.append(currDate)
        values.append(currValue)
        messages.append(' '.join(currMessage))

    if len(purchasesArray): categories = RunLLM(messages)

    output = [None] * len(purchasesArray)

    for index in range(len(purchasesArray)):
        output[index] = Purchase(values[index], categories[index], dates[index])

    return output

def groupPurchases(inputArray):
    categories = {"food_drink": 0.0,
                  "gas": 0.0,
                  "housing": 0.0,
                  "shopping": 0.0,
                  'subscriptions': 0.0,
                  'cash': 0.0,
                  'loans': 0.0,
                  "misc": 0.0}
    
    for purchase in inputArray:
        categories[purchase.category] += float(purchase.value)

    return categories

if __name__ == "__main__": main() 