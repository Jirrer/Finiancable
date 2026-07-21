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


def test_validate_user(seeded_db):
    with app_module.app.app_context():
        assert uploadTransaction.validateUser(1) == None

        with pytest.raises(exceptions.InvalidUser):
            uploadTransaction.validateUser(2)


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


def test_get_arrays_by_dict(seeded_db):
    dictData = {
        1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'group': 'income', 'category': 'salary'},
        2: {'value': 5.0, 'date': '2026-05-19', 'info': 'p', 'group': 'purchase', 'category': 'food'},
    }

    arrays = uploadTransaction.getTransactionsByGroup(dictData)

    assert 'income' in arrays and 'purchase' in arrays and 'transfer' in arrays
    assert isinstance(arrays['income'], list)
    assert isinstance(arrays['purchase'], list)
    assert arrays['income'][0] == (10.0, '2026-05-19', 'i', 'salary')
    assert arrays['purchase'][0] == (5.0, '2026-05-19', 'p', 'food')