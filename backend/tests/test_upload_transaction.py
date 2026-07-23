import pytest
import src.uploadTransaction as uploadTransaction
import src.exceptions as exceptions

import app as app_module
from models import db, Purchase, Transfer, Income

def test_run_invalid_data_type(seeded_db):
    # String
    with pytest.raises(exceptions.BadUploadType):
        uploadTransaction.run(1, "")

    # Int
    with pytest.raises(exceptions.BadUploadType):
        uploadTransaction.run(2, 1)

    # Tuple
    with pytest.raises(exceptions.BadUploadType):
            uploadTransaction.run(2, ())

def test_get_data_type(seeded_db):
    # Good Type
    assert uploadTransaction.getDataType({
        1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'group': 'income', 'category': 'payroll'},
        2: {'value': 5.0, 'date': '2026-05-19', 'info': 'p', 'group': 'purchase', 'category': 'food_drink'},
    }) == uploadTransaction.DataType.JSON

    # Bad types
    with pytest.raises(exceptions.BadUploadType):
        uploadTransaction.getDataType('')

    with pytest.raises(exceptions.BadUploadType):
        uploadTransaction.getDataType([])

    with pytest.raises(exceptions.BadUploadType):
        uploadTransaction.getDataType(1)

def test_validate_user(seeded_db):
    with app_module.app.app_context():
        assert uploadTransaction.validateUser(1) == None

        with pytest.raises(exceptions.InvalidUser):
            uploadTransaction.validateUser(2)

        with pytest.raises(ValueError):
            uploadTransaction.validateUser("1")

def test_validate_data(seeded_db):
    # Good Data
    assert uploadTransaction.validateData({
        1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'group': 'income', 'category': 'payroll'},
        2: {'value': 5.0, 'date': '2026-05-19', 'info': 'p', 'group': 'purchase', 'category': 'food_drink'},
    }, uploadTransaction.DataType.JSON) == None

    # Bad DataType
    with pytest.raises(Exception):
        uploadTransaction.validateData({
        1: {'value': 10.0, 'date': '2026-05-19', 'info': 'i', 'group': 'income', 'category': 'payroll'},
        2: {'value': 5.0, 'date': '2026-05-19', 'info': 'p', 'group': 'purchase', 'category': 'food_drink'},
    }, 'JSON')

def test_validate_data_json(seeded_db):
    ### Good Json ###
    assert uploadTransaction.run(1, {
        1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
        2: {'value': 12.1, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
        3: {'value': -1.15, 'date': '2026-05-19', 'info': "test information", 'group': 'transfer', 'category': 'transfer'},
    }) == None

    ### Bad Formats ###
    # Value
    with pytest.raises(exceptions.BadUploadData):
        uploadTransaction.run(1, {
            1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            2: {'value': 12, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            3: {'value': -1.15, 'date': '2026-05-19', 'info': "test information", 'group': 'transfer', 'category': 'transfer'},
        })

    # Date
    with pytest.raises(exceptions.BadDateInput):
        uploadTransaction.run(1, {
            1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            2: {'value': 12.10, 'date': '2026.05.19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            3: {'value': -1.15, 'date': '2026-05-19', 'info': "test information", 'group': 'transfer', 'category': 'transfer'},
        })

    # Info
    with pytest.raises(exceptions.BadUploadData):
        uploadTransaction.run(1, {
            1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            2: {'value': 12.1, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            3: {'value': -1.15, 'date': '2026-05-19', 'info': tuple("test information"), 'group': 'transfer', 'category': 'transfer'},
        })

    # Group
    with pytest.raises(exceptions.BadUploadData):
        uploadTransaction.run(1, {
            1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'invalidGroup': 'purchase', 'category': 'misc'},
            2: {'value': 12.1, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            3: {'value': -1.15, 'date': '2026-05-19', 'info': "test information", 'group': 'transfer', 'category': 'transfer'},
        })
    # Category
    with pytest.raises(exceptions.BadUploadData):
        uploadTransaction.run(1, {
            1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            2: {'value': 12.1, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'badCategory'},
            3: {'value': -1.15, 'date': '2026-05-19', 'info': "test information", 'group': 'transfer', 'category': 'transfer'},
        })

def test_run_json(seeded_db):
    # Assumed Valid Data 
    with app_module.app.app_context():
        uploadTransaction.run(1, {
            1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
            2: {'value': 27.15, 'date': '2026-05-19', 'info': "lunch", 'group': 'purchase', 'category': 'food_drink'},
            3: {'value': -5.00, 'date': '2026-05-18', 'info': "transfer to savings", 'group': 'transfer', 'category': 'transfer'},
            4: {'value': 1000.50, 'date': '2026-05-01', 'info': "paycheck", 'group': 'income', 'category': 'payroll'},
            5: {'value': 12.75, 'date': '2026-05-20', 'info': "coffee", 'group': 'purchase', 'category': 'food_drink'},
            6: {'value': 1500.00, 'date': '2026-04-30', 'info': "salary", 'group': 'income', 'category': 'payroll'},
            7: {'value': -200.00, 'date': '2026-05-10', 'info': "rent transfer", 'group': 'transfer', 'category': 'transfer'},
            8: {'value': 5.99, 'date': '2026-05-21', 'info': "snack", 'group': 'purchase', 'category': 'misc'},
            9: {'value': 500.25, 'date': '2026-05-05', 'info': "bonus", 'group': 'income', 'category': 'payroll'},
            10: {'value': 8.25, 'date': '2026-05-19', 'info': "bus fare", 'group': 'purchase', 'category': 'misc'},
            11: {'value': -1.00, 'date': '2026-05-19', 'info': "rounding transfer", 'group': 'transfer', 'category': 'transfer'},
            12: {'value': 100.00, 'date': '2026-05-03', 'info': "groceries", 'group': 'purchase', 'category': 'food_drink'},
            13: {'value': 250.00, 'date': '2026-05-11', 'info': "side gig", 'group': 'income', 'category': 'payroll'},
            14: {'value': 3.50, 'date': '2026-05-19', 'info': "water", 'group': 'purchase', 'category': 'misc'},
            15: {'value': 60.00, 'date': '2026-05-02', 'info': "tool", 'group': 'purchase', 'category': 'misc'},
            16: {'value': 45.00, 'date': '2026-05-06', 'info': "book", 'group': 'purchase', 'category': 'misc'},
            17: {'value': -50.00, 'date': '2026-05-07', 'info': "pay back", 'group': 'transfer', 'category': 'transfer'},
            18: {'value': 75.00, 'date': '2026-05-08', 'info': "freelance", 'group': 'income', 'category': 'payroll'},
            19: {'value': 20.00, 'date': '2026-05-09', 'info': "gift", 'group': 'income', 'category': 'payroll'},
            20: {'value': 300.00, 'date': '2026-05-12', 'info': "project", 'group': 'income', 'category': 'payroll'},
        })
        
        assert Purchase.query.filter_by(user_id=1).count() == 9
        assert Transfer.query.filter_by(user_id=1).count() == 4
        assert Income.query.filter_by(user_id=1).count() == 7

def test_group_json_transactions(seeded_db):
    # Assumed Valid Data
    arrays = uploadTransaction.groupJsonTransactions({
        1: {'value': 27.15, 'date': '2026-05-19', 'info': "test information", 'group': 'purchase', 'category': 'misc'},
        2: {'value': 27.15, 'date': '2026-05-19', 'info': "lunch", 'group': 'purchase', 'category': 'food_drink'},
        3: {'value': -5.00, 'date': '2026-05-18', 'info': "transfer to savings", 'group': 'transfer', 'category': 'transfer'},
        4: {'value': 1000.50, 'date': '2026-05-01', 'info': "paycheck", 'group': 'income', 'category': 'payroll'},
        5: {'value': 12.75, 'date': '2026-05-20', 'info': "coffee", 'group': 'purchase', 'category': 'food_drink'},
        6: {'value': 1500.00, 'date': '2026-04-30', 'info': "salary", 'group': 'income', 'category': 'payroll'},
        7: {'value': -200.00, 'date': '2026-05-10', 'info': "rent transfer", 'group': 'transfer', 'category': 'transfer'},
        8: {'value': 5.99, 'date': '2026-05-21', 'info': "snack", 'group': 'purchase', 'category': 'misc'},
        9: {'value': 500.25, 'date': '2026-05-05', 'info': "bonus", 'group': 'income', 'category': 'payroll'},
        10: {'value': 8.25, 'date': '2026-05-19', 'info': "bus fare", 'group': 'purchase', 'category': 'misc'},
        11: {'value': -1.00, 'date': '2026-05-19', 'info': "rounding transfer", 'group': 'transfer', 'category': 'transfer'},
        12: {'value': 100.00, 'date': '2026-05-03', 'info': "groceries", 'group': 'purchase', 'category': 'food_drink'},
        13: {'value': 250.00, 'date': '2026-05-11', 'info': "side gig", 'group': 'income', 'category': 'payroll'},
        14: {'value': 3.50, 'date': '2026-05-19', 'info': "water", 'group': 'purchase', 'category': 'misc'},
        15: {'value': 60.00, 'date': '2026-05-02', 'info': "tool", 'group': 'purchase', 'category': 'misc'},
        16: {'value': 45.00, 'date': '2026-05-06', 'info': "book", 'group': 'purchase', 'category': 'misc'},
        17: {'value': -50.00, 'date': '2026-05-07', 'info': "pay back", 'group': 'transfer', 'category': 'transfer'},
        18: {'value': 75.00, 'date': '2026-05-08', 'info': "freelance", 'group': 'income', 'category': 'payroll'},
        19: {'value': 20.00, 'date': '2026-05-09', 'info': "gift", 'group': 'income', 'category': 'payroll'},
        20: {'value': 300.00, 'date': '2026-05-12', 'info': "project", 'group': 'income', 'category': 'payroll'},
    })

    # Validating Groups
    assert 'income' in arrays and 'purchase' in arrays and 'transfer' in arrays
    assert isinstance(arrays['income'], list)
    assert isinstance(arrays['purchase'], list)

    ### Validating Values
    # Purchase
    assert arrays['purchase'][0] == (27.15, '2026-05-19', 'test information', 'misc')
    assert arrays['purchase'][5] == (100.00, '2026-05-03', 'groceries', 'food_drink')

    # Income
    assert arrays['income'][1] == (1500.00, '2026-04-30', 'salary', 'payroll')
    assert arrays['income'][2] == (500.25, '2026-05-05', 'bonus', 'payroll')

    # Transfer
    assert arrays['transfer'][0] == (-5.00, '2026-05-18', 'transfer to savings', 'transfer')
    assert arrays['transfer'][3] == (-50.00, '2026-05-07', 'pay back', 'transfer')