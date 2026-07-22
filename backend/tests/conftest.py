import io, pytest, os

from werkzeug.datastructures import FileStorage

os.environ["DATABASE_LOCATION"] = ""
os.environ["DATABASE_URL"] = "sqlite:///Financeable_test.db"

import app as app_module
from models import db as _db, User

@pytest.fixture(scope="session")
def app():
    app_module.app.config["TESTING"] = True
    app_module.app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:/// Financeable_test.db"
        
    with app_module.app.app_context():
        _db.create_all()
        yield app_module.app
        _db.drop_all()


@pytest.fixture(autouse=True)
def clean_db():
    yield
    with app_module.app.app_context():
        _db.session.rollback()
        _db.session.expire_all()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture
def seeded_db():
    with app_module.app.app_context():
        user = User(username="testuser", password="password", email="test@example.com")
        _db.session.add(user)
        _db.session.commit()
    return _db


@pytest.fixture
def client(app):
    with app_module.app.test_client() as c:
        with c.session_transaction() as sess:
            sess.clear()
        yield c


@pytest.fixture
def mock_valid_csv_file():
    csv_data = """Date,Description,Amount
2024-01-15,Coffee Shop,-5.00
2024-01-16,Grocery Store,-45.50
"""
    def _make():
        return FileStorage(
            stream=io.BytesIO(csv_data.encode("utf-8")),
            filename="test.csv",
            content_type="text/csv",
        )
    return _make


@pytest.fixture
def mock_no_header_csv_file():
    csv_data = """2o2o-01-15,Gas,27.32
z0z4-01-15,Coffee Shop,-5.00
2024-01-16,Grocery Store,-45.50
"""
    def _make():
        return FileStorage(
            stream=io.BytesIO(csv_data.encode("utf-8")),
            filename="test.csv",
            content_type="text/csv",
        )
    return _make

@pytest.fixture
def mock_bad_date_csv_file():
    csv_data = """Date,Description,Amount
zoz4-01-15,Coffee Shop,-5.00
2024-o1-16,Grocery Store,-45.50
"""
    def _make():
        return FileStorage(
            stream=io.BytesIO(csv_data.encode("utf-8")),
            filename="test.csv",
            content_type="text/csv",
        )
    return _make


@pytest.fixture
def mock_get_transactions(monkeypatch):
    def fake_run(report, returnType):
        return [
            {"date": "2024-01-15", "description": "Coffee Shop", "amount": -5.00}
        ]
    import src.getTransactions as gt
    monkeypatch.setattr(gt, "run", fake_run)
    return fake_run


@pytest.fixture
def mock_valid_user(monkeypatch):
    import src.uploadTransaction as ut
    monkeypatch.setattr(ut, "validateUser", lambda uid: True)
    return True