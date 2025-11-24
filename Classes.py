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
