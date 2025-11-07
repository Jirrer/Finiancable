import os, json
from datetime import datetime
from pypdf import PdfReader


def isDate(string: str):
    formats = ["%m-%d", "%m-%d-%Y", "%m-%d-%y", "%m/%d", "%m/%d/%Y", "%m/%d/%y"]
    for fmt in formats:
        try:
            datetime.strptime(string, fmt)
            return True
        except ValueError:
            continue
    return False

def isFloat(string: str):
    try:
        float(string)
        return '.' in string
    except ValueError:
        return False

def getThisMonth() -> str:
    now = datetime.now()
    month = now.month  
    year = now.year 

    return (f'{month}/{year}')

def labelToDate(label: str) -> str:
    year = label[0:4]
    month = label[5:7]

    return f'{month}/{year}'