from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib, csv, sqlite3
from typing import List, Tuple
from ParsePDFs import parsePdf


def RunLLM(strings: list) -> list:
    vectorizer = joblib.load("data\\vectorizer.joblib")

    clf = joblib.load("data\\classifier.joblib")

    predictions = clf.predict(vectorizer.transform(strings))
    
    return predictions

def TrainModel():
    texts, labels = [], []

    purchasesArray = parsePdf(['data\\TrainingData.PDF'])

    for purchase in purchasesArray:
        texts.append(purchase[2])
        labels.append(input(f"{purchase}: "))

    newModel = (texts, labels)

    TrainLLM(newModel)

def TrainLLM(newModel: Tuple[List[str], List[str]]):
    connection = sqlite3.connect('data\\Financeable.db')

    cursor = connection.cursor()

    oldText, oldLabels = pullFromDatabase(cursor)

    newText, newLabels = newModel[0], newModel[1]

    if len(newText) != len(newLabels):
        print("Number of Labels does not match number of texts!")
        return

    oldText.extend(newText)
    oldLabels.extend(newLabels)

    finalText, finalLabels = oldText, oldLabels

    if finalText and finalLabels:
        pushToDatabase(cursor, newText, newLabels)

        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(finalText)

        clf = MultinomialNB()
        clf.fit(X, finalLabels)

        joblib.dump(vectorizer,"data\\vectorizer.joblib")
        joblib.dump(clf, "data\\classifier.joblib")

        print("Model trained and saved successfully!")
    else:
        joblib.dump('',"data\\vectorizer.joblib")
        joblib.dump('', "data\\classifier.joblib")

    connection.commit()
    connection.close()


def pullFromDatabase(cursor) -> tuple:
    cursor.execute("SELECT text, label FROM ML_data")

    rows = cursor.fetchall()

    try:
        textOutput, labelOutput = zip(*rows)

        textOutput = list(textOutput)
        labelOutput = list(labelOutput)

        return (textOutput, labelOutput)
    
    except ValueError:
        return ([], [])

def pushToDatabase(cursor, newTexts, newLables):
    cursor.executemany("INSERT INTO ML_data (text, label) VALUES (?, ?)", list(zip(newTexts, newLables)))


def ClearLLM():
    verification = input("Are you sure you want to reset the model data? (This action cannot be undone)\nType 'clear model data': ")

    if verification == 'clear model data':
        connection = sqlite3.connect('data\\Financeable.db')

        curser = connection.cursor()

        curser.execute("DELETE FROM ML_data")
        curser.execute("DELETE FROM sqlite_sequence WHERE name='ML_data'")

        connection.commit()

        curser.execute("VACUUM")

        connection.close()

        TrainLLM(([], []))

        print("Model Reset.")
    
    else:
        print("Kept Model")