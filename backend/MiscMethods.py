from datetime import datetime

def isDate(string):
    formats = ["%m-%d", "%m-%d-%Y", "%m-%d-%y", "%m/%d", "%m/%d/%Y", "%m/%d/%y"]
    for fmt in formats:
        try:
            datetime.strptime(string, fmt)
            return True
        except ValueError:
            continue
    return False