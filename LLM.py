import joblib, os, sqlite3
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from typing import List, Tuple

from dotenv import load_dotenv

load_dotenv()

def RunLLM(strings: list) -> list:
    vectorizer = joblib.load(os.getenv('VECTORIZER_LOCATION'))
    clf = joblib.load(os.getenv('CLASSIFIER_LOCATION'))

    return clf.predict(vectorizer.transform(strings))
    
# def TrainModelLosses():
#     rawData = pullData('training')
#     losses = pullContent(rawData, 'lossess_regex')

#     texts, labels = [], []

#     for purchase in losses:
#         texts.append(purchase[2])
#         labels.append(input(f"{purchase}: "))

#     TrainLLM(texts, labels)

def TrainLLM(newTexts, newLabels):
    connection = sqlite3.connect(os.getenv('DATABASE_LOCATION'))

    cursor = connection.cursor()

    oldText, oldLabels = pullFromDatabase(cursor)

    if len(newTexts) != len(newLabels):
        print("Number of Labels does not match number of texts!")
        return

    oldText.extend(newTexts)
    oldLabels.extend(newLabels)

    finalText, finalLabels = oldText, oldLabels

    if finalText and finalLabels:
        pushToDatabase(cursor, newTexts, newLabels)

        vectorizer = TfidfVectorizer()
        X = vectorizer.fit_transform(finalText)

        clf = MultinomialNB()
        clf.fit(X, finalLabels)

        joblib.dump(vectorizer,os.getenv('VECTORIZER_LOCATION'))
        joblib.dump(clf, os.getenv('CLASSIFIER_LOCATION'))

        print("Model trained and saved successfully!")
    else:
        joblib.dump('', os.getenv('VECTORIZER_LOCATION'))
        joblib.dump('', os.getenv('CLASSIFIER_LOCATION'))

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
        connection = sqlite3.connect(os.getenv('DATABASE_LOCATION'))

        curser = connection.cursor()

        curser.execute("DELETE FROM ML_data")
        curser.execute("DELETE FROM sqlite_sequence WHERE name='ML_data'")

        connection.commit()

        curser.execute("VACUUM")

        connection.close()

        print("Model Reset.")
    
    else:
        print("Kept Model")