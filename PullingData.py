import re, os, json, io
from MiscMethods import isDate, isFloat, getThisMonth
from pypdf import PdfReader
from dotenv import load_dotenv
from typing import Literal
from ProccessingData import getRawPurchases, categorizePurchases
from Classes import Month_Report

load_dotenv()

with open(os.getenv('DATA_LOCATION'), 'r', encoding='utf-8') as file:
    jsonData = json.load(file)

async def pullRawData(rawInput):
    data = await rawInput.read()

    reader = PdfReader(io.BytesIO(data))

    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text

def getUserData():
    with open(os.getenv('USER_INFO_LOCATION'), 'r', encoding='utf-8') as file:
        return json.load(file)

def runMonthlyReport(monthYear: str):
    pdfs = getPreparedPdfs()

    rawPurchases = getRawPurchases(pdfs)
    categorizedPurchases = categorizePurchases(rawPurchases)

    monthReport = Month_Report(monthYear)

    monthReport.profit_loss = getProfit(categorizedPurchases)

    pushData(monthReport)

def getPreparedPdfs() -> list:
    output = []

    pdfLocation = os.getenv('PDF_LOCATION')

    pdfNames = [f for f in os.listdir(pdfLocation)]

    for file in pdfNames:
        if os.path.exists(f'{pdfLocation}\\{file}'):
            output.append((pullBankName(file), f'{pdfLocation}\\{file}'))

    return output
        
def pullBankName(fileName: str) -> str:
    output = []

    for letter in fileName:
        if letter == '#': return ''.join(output)

        output.append(letter)

    return "Error pulling bank name"

def getProfit(puchasesInput: list) -> float:
    total = 0.0

    for purchase in puchasesInput:
        if isFloat(purchase.value): total += float(purchase.value)
    
    return total

def pushData(report: Month_Report):
    filePath = os.getenv('USER_INFO_LOCATION')

    if os.path.exists(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []  # if file is empty
    else:
        data = []

    newMonth = {}
    newMonth["Profit/Loss"] = report.profit_loss

    data[report.date] = newMonth

    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return True

def clearPdfFolders():
    pdfLocation = os.getenv('PDF_LOCATION')

    files = [f for f in os.listdir(pdfLocation)]

    for fileLocation in files:
        if os.path.exists(f'{pdfLocation}\\{fileLocation}'):
            os.remove(f'{pdfLocation}\\{fileLocation}')

    return True