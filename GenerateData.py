import joblib, os, json, csv, re

with open('supported_banks.json', 'r', encoding='utf-8') as file:
    jsonData = json.load(file)

class Purchase:
    def __init__(self, purchaseValue, purchaseType, purchaseDate, purchaseInfo):
        self.value = purchaseValue
        self.category = purchaseType
        self.date = purchaseDate
        self.info = purchaseInfo

class Month_Report:
    def __init__(self, date):
        self.date = date
        self.loss = None
        self.gain = None
        self.profit_loss = None
        self.categories = {}

    def updateCategories(self, purchases: list):
        for purchase in purchases:
            if purchase.category in self.categories:
                self.categories[purchase.category] += float(purchase.value)
            else:
                self.categories[purchase.category] = float(purchase.value)

def main(vectorizer, clf, monthYear: str):
    csvFileLocations = getFileLocations()
    
    rawLosses, rawGains = getRawPurchases(csvFileLocations)

    categorizedPurchases = categorizePurchases(rawLosses, clf, vectorizer)

    monthReport = Month_Report(monthYear)

    monthReport.loss = getLoss(categorizedPurchases)

    monthReport.gain = getGain(rawGains)

    monthReport.profit_loss = monthReport.gain + monthReport.loss

    monthReport.updateCategories(categorizedPurchases)

    pushData(monthReport)



def getFileLocations() -> list:
    output = []

    pdfLocation = 'ReportData'

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

def getRawPurchases(csvFiles: list):
    losses, gains = [], []
    
    for bank, filePath in csvFiles:
        with open(filePath, 'r', newline='') as file:
            reader = csv.reader(file)

            next(reader)

            dateIndex, infoIndex, valueIndex = None, None, None

            bankFormat = jsonData[bank]['format']
            bannedPayments = jsonData[bank]['skipped_data']

            reversePayents = jsonData[bank]['reverseValues']
            
            for index in range(len(bankFormat)):
                if bankFormat[index] == 'date': dateIndex = index
                elif bankFormat[index] == 'info': infoIndex = index
                elif bankFormat[index] == 'value': valueIndex = index

            for row in reader:
                rowDate = row[dateIndex]
                rowInfo = row[infoIndex]

                if (reversePayents):
                    rowValue = f'-{row[valueIndex]}'
                else:
                    rowValue = row[valueIndex]

                if float(rowValue) < 0:
                    losses.append(Purchase(rowValue, None, rowDate, rowInfo))
                else:
                    gains.append(Purchase(rowValue, None, rowDate, rowInfo))

    return (losses, gains)


def categorizePurchases(purchases: list, clf, vectorizer) -> list:
    infoStrs = [purchase.info for purchase in purchases]

    strsCategories = clf.predict(vectorizer.transform(infoStrs))

    for index in range(len(purchases)):
        purchases[index].category = strsCategories[index]

    return purchases

def getLoss(puchasesInput: list) -> float:
    total = 0.0

    for purchase in puchasesInput:
        if isFloat(purchase.value): total += float(purchase.value)
    
    return total

def getGain(purchasesInput: list):
    total = 0.0
    
    for purchase in purchasesInput:
        if float(purchase.value) > 0:
            total += float(purchase.value)

    return total


def isFloat(string: str):
    try:
        float(string)
        return '.' in string
    except ValueError:
        return False

def pushData(report: Month_Report):
    filePath = 'data\\userInfo.json'

    if os.path.exists(filePath):
        with open(filePath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []  # if file is empty
    else:
        data = []

    newMonth = {}
    
    newMonth["Losses"] = report.loss

    newMonth["Gains"] = report.gain

    newMonth["Profit/Loss"] = report.profit_loss

    newMonth["Categories"] = report.categories

    data[report.date] = newMonth

    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return True
    
if __name__ == "__main__":
    vectorizer = joblib.load('data\\vectorizer.joblib'); print("Pulled vectorizer.")

    clf = joblib.load('data\\classifier.joblib'); print("Pulled clf.")

    main(vectorizer, clf, "12/2025"); print("Ran Report")