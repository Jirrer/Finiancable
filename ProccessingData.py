import csv, dotenv, json, os
from Classes import Purchase
from LLM import RunLLM

dotenv.load_dotenv()

with open(os.getenv('SUPPORTED_BANKS'), 'r', encoding='utf-8') as file:
    jsonData = json.load(file)


def getRawPurchases(csvFiles: list) -> list:
    output = []
    
    for bank, filePath in csvFiles:
        with open(filePath, 'r', newline='') as file:
            reader = csv.reader(file)

            next(reader)

            dateIndex, infoIndex, valueIndex = None, None, None

            bankFormat = jsonData[bank]['format']
            bannedPayments = jsonData[bank]['skipped_data']
            
            for index in range(len(bankFormat)):
                if bankFormat[index] == 'date': dateIndex = index
                elif bankFormat[index] == 'info': infoIndex = index
                elif bankFormat[index] == 'value': valueIndex = index

            for row in reader:
                rowDate = row[dateIndex]
                rowInfo = row[infoIndex]
                rowValue = row[valueIndex]

                if rowInfo in bannedPayments: continue

                output.append(Purchase(rowValue, None, rowDate, rowInfo))

    return output

def categorizePurchases(purchases: list) -> list:
    infoStrs = [purchase.info for purchase in purchases]

    strsCategories = RunLLM(infoStrs)

    for index in range(len(purchases)):
        purchases[index].category = strsCategories[index]

    return purchases