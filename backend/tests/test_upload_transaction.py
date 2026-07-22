import pytest
import src.uploadTransaction as uploadTransaction
import src.exceptions as exceptions

import app as app_module
from models import db, Purchase, Transfer


def test_run(seeded_db):
    dictData = {
        1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
        2: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
        3: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'transfer', 'category': 'misc'},
    }

    with app_module.app.app_context():
        with pytest.raises(exceptions.BadUploadType):
            uploadTransaction.run(1, list(dictData))

        with pytest.raises(exceptions.InvalidUser):
            uploadTransaction.run(2, dictData)

def test_get_data_type(seeded_db):
    dictData = {
        1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'group': 'income', 'category': 'salary'},
        2: {'value': 5.0, 'date': '2026-05-19', 'info': 'p', 'group': 'purchase', 'category': 'food'},
    }

    assert uploadTransaction.getDataType(dictData) == uploadTransaction.DataType.JSON

    with pytest.raises(exceptions.BadUploadType):
        uploadTransaction.getDataType('')

def test_validate_user(seeded_db):
    with app_module.app.app_context():
        assert uploadTransaction.validateUser(1) == None

        with pytest.raises(exceptions.InvalidUser):
            uploadTransaction.validateUser(2)

        with pytest.raises(ValueError):
            uploadTransaction.validateUser("1")

def test_validate_data(seeded_db):
    dictData = {
            1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'group': 'income', 'category': 'salary'},
            2: {'value': 5.0, 'date': '2026-05-19', 'info': 'p', 'group': 'purchase', 'category': 'food'},
        }
    
    badDictData = { 1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'badValue': 'income', 'category': 'salary'}}

    assert uploadTransaction.validateData(dictData, uploadTransaction.DataType.JSON) == None

    with pytest.raises(Exception):
        uploadTransaction.validateData(dictData, 'bad_value')

    with pytest.raises(exceptions.BadUploadData):
        uploadTransaction.validateData(badDictData, uploadTransaction.DataType.JSON)

def test_validate_data_json(seeded_db):
    dictData = {
        1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'group': 'income', 'category': 'salary'},
        2: {'value': 5.0, 'date': '2026-05-19', 'info': 'p', 'group': 'purchase', 'category': 'food'},
    }

    badDictData = { 1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'badValue': 'income', 'category': 'salary'}}

    assert uploadTransaction.validateData_json(dictData) == None

    with pytest.raises(exceptions.BadUploadData):
        uploadTransaction.validateData_json(badDictData)

def test_run_by_type(seeded_db):
    assert uploadTransaction.runByType(1, {}, uploadTransaction.DataType.JSON) == None

    with pytest.raises(Exception):
        uploadTransaction.runByType(1, '', 'Bad_Upload_Type')

def test_run_json(seeded_db):
    dictData = {
        1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
        2: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
        3: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'transfer', 'category': 'misc'},
    }

    with app_module.app.app_context():
        uploadTransaction.run(1, dictData)

        purchases = Purchase.query.filter_by(user_id=1).count()
        transfers = Transfer.query.filter_by(user_id=1).count()

    assert purchases == 2
    assert transfers == 1

def test_group_json_transactions(seeded_db):
    dictData = {
        1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'group': 'income', 'category': 'salary'},
        2: {'value': 5.0, 'date': '2026-05-19', 'info': 'p', 'group': 'purchase', 'category': 'food'},
    }

    badDictData = { 1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'badValue': 'income', 'category': 'salary'}}

    arrays = uploadTransaction.groupJsonTransactions(dictData)

    assert 'income' in arrays and 'purchase' in arrays and 'transfer' in arrays
    assert isinstance(arrays['income'], list)
    assert isinstance(arrays['purchase'], list)
    assert arrays['income'][0] == (10.0, '2026-05-19', 'i', 'salary')
    assert arrays['purchase'][0] == (5.0, '2026-05-19', 'p', 'food')

    with pytest.raises(KeyError):
        uploadTransaction.groupJsonTransactions(badDictData)