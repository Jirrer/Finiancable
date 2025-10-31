import re, os, json
from Classes import Purchase
from MiscMethods import isDate, isFloat
from pypdf import PdfReader
from dotenv import load_dotenv
from typing import Literal

# Issue - skipped netflix because it did not have a card number with it
# To-Do: refactor again (later)

load_dotenv()

with open(os.getenv('DATA_LOCATION'), 'r', encoding='utf-8') as file:
    jsonData = json.load(file)

def pullLosses() -> dict:
    rawLosses = pullData('losses')
    purchases = pullContent(rawLosses, 'lossess_regex')
    finalPurchases = categorisePurchases(purchases)
    categoriesDict = groupPurchases(finalPurchases)

    return categoriesDict

def pullGains() -> dict:
    rawGains = pullData('gains')
    gains = pullContent(rawGains, 'gains_regex')
    profit = getProfit(gains)

    return profit

def getProfit(gainsInput):
    total = 0.0

    for gain in gainsInput:
        processedGain = gain.replace('$','')
        processedGain = processedGain.split(' ')
        
        for x in processedGain:
            if isFloat(x): total += float(x)
    
    return total

def pullData(parseType: Literal['losses', 'gains', 'training']):
    if parseType == 'losses': folderPath = os.getenv('LOSS_PDF_LOCATION')
    elif parseType == 'gains': folderPath = os.getenv("GAIN_PDF_LOCATION")
    elif parseType == 'training': folderPath = os.getenv('TRAINING_DATA_LOCATION')

    pdfLocations = [filePath for filePath in os.listdir(folderPath)]

    pdfReadersArray = [PdfReader(f"{folderPath}\\{pdf}") for pdf in pdfLocations]

    pdfContent = []

    for reader in pdfReadersArray:
        if reader.is_encrypted:
            reader.decrypt('') # <---------- fix

        numPages = PdfReader.get_num_pages(reader)

        for index in range(numPages):
            page = reader.pages[index]

            pdfContent.append(page.extract_text())


    pdfsOutput = ''.join(pdfContent).split("\n")

    return pdfsOutput

def pullContent(rawContent: str, regexType: Literal['lossess_regex', 'gains_regex']):
    content = []

    for contentRegex in jsonData[regexType]:
        content.append(
            (
                re.compile(contentRegex['regex']),
                lambda text: re.sub(
                    contentRegex['normalize'],
                    contentRegex['output'],
                    text
                )
            )
        )

    foundOutput = [] 

    for textContent in rawContent:
        for regex in content:
            pattern, normalizer = regex

            cleanedText = normalizer(textContent)   

            found = pattern.findall(cleanedText)

            for match in found:
                foundOutput.append(match)

    return foundOutput


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