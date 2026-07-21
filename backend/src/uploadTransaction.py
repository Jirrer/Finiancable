from dotenv import load_dotenv
from datetime import date as date_type

import src.exceptions as exceptions

from models import db, Purchase, Transfer, Income, User


load_dotenv()

MODEL_MAP = {
    'income': Income,
    'purchase': Purchase,
    'transfer': Transfer,
}

def run(userID: int, data):

    validateUser(userID, data)
    
def validateUser(potentialID: int, data) -> None | exceptions.InvalidUser | ValueError:
    if type(potentialID) != int:
        raise ValueError
    
    if db.session.get(User, potentialID) is None:
        raise exceptions.InvalidUser()

    runByType(potentialID, data)

def runByType(userID: int, data) -> None | exceptions.BadUploadType:
    match(data):
        case dict(): runJson(userID, data)
        case _: raise exceptions.BadUploadType(f'Type ({type(data)}) is not allowed')

def runJson(userID: int, data: dict[dict]):
    transactionsByGroup: dict[list[tuple]] = getTransactionsByGroup(data)

    for group, transactions in transactionsByGroup.items():
        model = MODEL_MAP[group]
        db.session.bulk_insert_mappings(model, [
            {
                'user_id': userID,
                'value': t[0],
                'date': date_type.fromisoformat(t[1]),
                'info': t[2],
                'category': t[3],
            }
            for t in transactions
        ])

    db.session.commit()

def getTransactionsByGroup(data: dict[dict]) -> dict[list[tuple]]:
    output = {'income': [], 'purchase': [], 'transfer': []}

    for transaction in data.values():
        try:
            if transaction['group'].lower() not in output.keys():
                print('could not find group')
                continue

            output[transaction['group']].append((
                transaction['value'],
                transaction['date'],
                transaction['info'],
                transaction['category']
            ))

        except KeyError:
            print("could not find value")
            continue

    return output