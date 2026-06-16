from dotenv import load_dotenv
from sqlalchemy import text, union_all, select, literal

from models import *

load_dotenv()

def run(userID: int) -> dict:
    allData = pullAllData(userID)
    
    output = {
        "NetWorth": calculateNetworth(allData),
        "Salary": findSalary(allData),
        "Emergency Fund": getEmergencyFund(allData)
    }

    return output

def pullAllData(userID: int):
    purchases = select(
        literal('purchase').label('type'),
        Purchase.id,
        Purchase.date,
        Purchase.category,
        Purchase.value,
        Purchase.info
    ).where(Purchase.user_id == userID)

    incomes = select(
        literal('income').label('type'),
        Income.id,
        Income.date,
        Income.category,
        Income.value,
        Income.info
    ).where(Income.user_id == userID)

    transfers = select(
        literal('transfer').label('type'),
        Transfer.id,
        Transfer.date,
        Transfer.category,
        Transfer.value,
        Transfer.info
    ).where(Transfer.user_id == userID)

    query = union_all(purchases, incomes, transfers).order_by(text('date DESC'))

    return db.session.execute(query).fetchall()

def calculateNetworth(allData: list[tuple]) -> dict:
    # cash = sum()
    # savings = sum()
    # retirement = sum()
    # losses = sum()
    networth = sum(x[4] for x in allData)

    return {
        "Networth": networth
    }

# To-Do: maybe figure out if there is more than one employer
def findSalary(allData: list[tuple]):
    validPayments = [x for x in allData if x[0] == 'income' and x[3] == 'payroll']

    byYearMonth = {}

    for payment in validPayments:
        yearMonth = payment[2].strftime('%Y-%m')

        if yearMonth in byYearMonth:
            byYearMonth[yearMonth] += payment[4]
        
        else:
            byYearMonth[yearMonth] = payment[4]

    salaryTotal = 0.0

    foundMonths = 0

    for yearMonth in reversed(list(byYearMonth)):
        salaryTotal += byYearMonth[yearMonth]

        foundMonths += 1

        if foundMonths == 12:
            break

    return round((salaryTotal // foundMonths) * 12)


def getEmergencyFund(allData: list[tuple]) -> tuple[float, float]:
    validLosses = [x for x in allData if x[0] != 'income']

    byYearMonth = {}

    for transaction in validLosses:
        yearMonth = transaction[2].strftime('%Y-%m')

        if yearMonth in byYearMonth:
            byYearMonth[yearMonth] += transaction[4]
        
        else:
            byYearMonth[yearMonth] = transaction[4]

    expensesTotal = 0.0

    foundMonths = 0

    for yearMonth in reversed(list(byYearMonth)):
        expensesTotal += byYearMonth[yearMonth]

        foundMonths += 1

        if foundMonths == 12:
            break


    livingExpense = round((abs(expensesTotal) // foundMonths))

    return round(abs(livingExpense * 3)), round(abs(livingExpense * 6))
    
if __name__ == "__main__":
    print(run(1))