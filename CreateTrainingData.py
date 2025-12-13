from GenerateData import getRawPurchases, getFileLocations

FILE_LOCATION = 'data\\Training_Data.csv' 

def main():
    data = createData()
    pushData(data)

def createData() -> list:
    output = []

    rawPurchases = getRawPurchases(getFileLocations())[0]

    for purchase in rawPurchases:
        output.append(f"ADD_LABEL,{purchase.info}")

    return output

def pushData(data: list):
    with open(FILE_LOCATION, "w", newline="", encoding="utf-8") as file:
        for line in data:
            file.write(line + "\n")

        print("Created Training Data.")

if __name__ == "__main__": 
    main()