from dotenv import load_dotenv
from datetime import date
from enum import Enum, auto

import src.exceptions as exceptions

from models import db, Purchase, Transfer, Income, User

load_dotenv()

MODEL_MAP = {
    'income': Income,
    'purchase': Purchase,
    'transfer': Transfer,
}

class DataType(Enum):
    JSON = auto()

def run(userID: int, data):
    dataType = getDataType(data)

    validateUser(userID)

    validateData(data, dataType)
    
    runByType(userID, data, dataType)

def getDataType(data) -> DataType | exceptions.BadUploadType:
    match(data):
        case dict(): return DataType.JSON
        case _: raise exceptions.BadUploadType(f'Type ({type(data)}) is not allowed')

def validateUser(potentialID: int) -> None | exceptions.InvalidUser | ValueError:
    if type(potentialID) != int:
        raise ValueError
    
    if db.session.get(User, potentialID) is None:
        raise exceptions.InvalidUser()
    
def validateData(data, dataType: DataType) -> None | exceptions.BadUploadData | exceptions.BadUploadData:
    match(dataType):
        case DataType.JSON: validateData_json(data)
        case _: raise Exception

def validateData_json(data):
    allowedKeys = ('value', 'date', 'info', 'group', 'category')

    for transaction in data.values():
        for key in transaction.keys():
            if key not in allowedKeys: raise exceptions.BadUploadData

def runByType(userID: int, data, dataType: DataType) -> None | exceptions.BadUploadType:
    match(dataType):
        case DataType.JSON: runJson(userID, data)
        case _: raise Exception

def runJson(userID: int, data: dict[dict]):
    transactionsByGroup: dict[list[tuple]] = groupJsonTransactions(data)

    for group, transactions in transactionsByGroup.items():
        model = MODEL_MAP[group]
        db.session.bulk_insert_mappings(model, [
            {
                'user_id': userID,
                'value': t[0],
                'date': date.fromisoformat(t[1]),
                'info': t[2],
                'category': t[3],
            }
            for t in transactions
        ])

    db.session.commit()

def groupJsonTransactions(data: dict[dict]) -> dict[list[tuple]]:
    output = {'income': [], 'purchase': [], 'transfer': []}

    for transaction in data.values():
        output[transaction['group']].append((
            transaction['value'],
            transaction['date'],
            transaction['info'],
            transaction['category']
        ))
    return output