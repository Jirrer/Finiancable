

### GenerateData.py



### TrainData.py

## CreateTrainingData.py
This file's goal is to create a blueprint for creating or adding training data. It pulls
every purchase (transaction with negative value) from the ReportData directory - by using methods from "GenerateData.py".
The purchases' info is used for the labels and a placeholder "ADD_LABEL" tag is added for each purchase. This tag can then
be manually updated to the correct category.
