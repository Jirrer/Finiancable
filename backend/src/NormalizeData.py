import re
from datetime import datetime

def formatDate(date: str) -> str:
    formats = [
        "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y",
        "%b %d, %Y", "%d-%m-%Y", "%m-%d-%Y", "%Y/%m/%d",
        "%d %B %Y", "%d %b %Y", "%m.%d.%Y", "%d.%m.%Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: '{date}'")

def isValidDate(possibleDate: str) -> bool:
    formats = ["%m/%d/%y", "%m-%d-%y", "%m/%d/%Y", "%m-%d-%Y", "%y/%m/%d", "%y-%m-%d", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"]
    
    for fmt in formats:
        try:
            datetime.strptime(possibleDate, fmt)
            return True
        
        except ValueError:
            continue
        
    return False

US_STATES = {
    "al","ak","az","ar","ca","co","ct","de","fl","ga","hi","id","il","in","ia","ks",
    "ky","la","me","md","ma","mi","mn","ms","mo","mt","ne","nv","nh","nj","nm","ny",
    "nc","nd","oh","ok","or","pa","ri","sc","sd","tn","tx","ut","vt","va","wa","wv","wi","wy"
}

def normalizePurchase(info: str):
    info = info.replace('\n', '')
    info = stripBankBoilerPlate(info)
    info = stripLocations(info)
    info = stripDates(info)
    info = stripSpecialChars(info)
    info = removeExtraSpace(info)

    return info

def stripBankBoilerPlate(text):
    text = text.replace('DEBIT CARD PURCHASE','')
    text = text.replace('MERCHANT PAYMENT','')

    return text

def stripStoreNumbers(text):
    text = re.sub(r'store\s*\d+', '', text)

    text = re.sub(r'#\s*\d+', '', text)

    text = re.sub(r'\b[a-z]-\d+\b', '', text)

    text = re.sub(r'\b\d{3,}\b', '', text)

    return text

def stripLocations(text):
    text = re.sub(r'\b\d{5}(-\d{4})?\b', '', text)

    text = re.sub(r'\b[a-z]+\s+(?:' + '|'.join(US_STATES) + r')\b', '', text) # City Patterns

    text = re.sub(r'\s+(' + '|'.join(US_STATES) + r')$', '', text)

    text = re.sub(r',.*$', '', text) # Comma Locations Sections

    return text

def stripDates(text):
    text = re.sub(r'\b\d{1,2}/\d{1,2}(/\d{2,4})?\b', '', text) # Slash Dates

    text = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '', text) # Dash Dates

    text = re.sub(r'\b\d{6,8}\b', '', text) # Companct Numbers

    text = re.sub(r'\b\d{4,}\b', '', text) # Long Numbers

    text = re.sub(r'x+\d*', '', text) # Masked Numbers

    return text

def stripSpecialChars(text):
    text = re.sub(r'\b[xX]{4,}[0-9]*[xX]*\b', '', text)

    return text

def removeExtraSpace(text):
    text = text.lower()

    text = re.sub(r'^[\s"\']+', '', text) # Extra Junk

    return text