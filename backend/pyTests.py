import ParsePDFs
import MiscMethods
import LLM

# ParsePDFs.main(["pdfs\\Statement2025-09-11.PDF", "pdfs\\9043929.pdf"])

 # <------------ need to start training from text file
text = [
]

labels = ['shopping',
        'misc',
        'misc',
        'gas',
        'food_drink',
        'shopping',
        'shopping',
        'misc',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'food_drink',
        'subscriptions',
        'gas'
]

newModel = (text, labels)

purchasesTest = [
    
]

# LLM.RunLLM(purchasesTest)
LLM.ClearLLM()
