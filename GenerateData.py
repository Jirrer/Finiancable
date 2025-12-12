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
        self.profit_loss = None

def main(vectorizer, clf, monthYear: str):
    csvFileLocations = getFileLocations()
    
    rawPurchases = getRawPurchases(csvFileLocations)

    categorizedPurchases = categorizePurchases(rawPurchases)

    monthReport = Month_Report(monthYear)

    monthReport.profit_loss = getProfit(categorizedPurchases)

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

def getRawPurchases(csvFiles: list) -> list:
    output = []
    
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

                if not isBannedPayment(bannedPayments, rowInfo):
                    output.append(Purchase(rowValue, None, rowDate, rowInfo))

    return output

def isBannedPayment(paymentList: list, paymentInfo: str):
    for search in paymentList:
        match = re.search(search, paymentInfo)

        if match: return True

    return False

def categorizePurchases(purchases: list) -> list:
    infoStrs = [purchase.info for purchase in purchases]

    strsCategories = clf.predict(vectorizer.transform(infoStrs))

    for index in range(len(purchases)):
        purchases[index].category = strsCategories[index]

    return purchases

def getProfit(puchasesInput: list) -> float:
    total = 0.0

    for purchase in puchasesInput:
        if isFloat(purchase.value): total += float(purchase.value)
    
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
    newMonth["Profit/Loss"] = report.profit_loss

    data[report.date] = newMonth

    with open(filePath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    return True
    
if __name__ == "__main__":
    vectorizer = joblib.load('data\\vectorizer.joblib'); print("Pulled vectorizer.")

    clf = joblib.load('data\\classifier.joblib'); print("Pulled clf.")

    main(vectorizer, clf, "12/2025"); print("Ran Report")