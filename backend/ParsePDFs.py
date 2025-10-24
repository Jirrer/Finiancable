from Classes import Purchase
from MiscMethods import isDate, isFloat
from pypdf import PdfReader
import re


# Issue - skipped netflix because it did not have a card number with it
# Issue training model


def main(pdfs: list):
    purchases = getPurchases(pdfs)
    categoriesDict = groupPurchases(purchases)

    # print(purchases)
    print(categoriesDict)

    for x in purchases:
        print(x.category)

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
            re.compile(r"(\d{2}/\d{2})\s+(\d+\.\d+)(.*?)(?=\s?FROM\s?CARD#:\s?X{12}\d{3}[X\d])"),
            lambda text: re.sub(
                r"(\d{2}/\d{2}\s+\d+\.\d+)(.*?)(?=\s?FROM\s?CARD#:\s?X{12}\d{3}[X\d])",
                r"\1 \2",
                text
            )
        ),

        (
            re.compile(r"(\d\d/\d\d)\s+(\d+\.\d\d)(.*?)(?=:?\s?TRUE ACH CO)"),
            lambda text: re.sub(
                r"(\d\d/\d\d)/\d\d\s+\d+\.\d\d\s+(\d+\.\d\d)\s+-\d+\.\d\d\s+(.*?)",
                r"\1 \2 \3",
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
    categories = {"food_drink": 0.0,
                  "gas": 0.0,
                  "housing": 0.0,
                  "shopping": 0.0,
                  'subscriptions': 0.0,
                  'cash': 0.0,
                  'loan': 0.0,
                  "misc": 0.0}
    
    for purchase in inputArray:
        categories[purchase.category] += float(purchase.value)

    return categories

if __name__ == "__main__": main() 