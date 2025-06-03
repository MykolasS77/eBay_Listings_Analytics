import pytest
from main import create_app, db
from main.database import SavedData

#code coverage command (while in root directory) 'pytest tests --cov-report term-missing --cov=src'.

@pytest.fixture()
def main_app():
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        db.init_app(app)
        db.create_all()

    yield app

@pytest.fixture()
def client(main_app):
    return main_app.test_client()

def test_request(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Search Parameter" in response.data

def test_search_without_selecting_markets(client, main_app):
    with main_app.app_context():
        response = client.post("/", data={
          "search_parameter": "epiphone electric guitar",
     }, follow_redirects=True)
        
        assert b'<form method="post" action="/generate-graph" class="inline">' in response.data
        assert response.status_code == 200
        assert SavedData.query.count() == 1

def test_search_with_markets(client, main_app):
    with main_app.app_context():
        response = client.post("/", data={
          "search_parameter": "epiphone electric guitar",
          "market": "['EBAY_GB', 'GBP']"
     }, follow_redirects=True)
        
        print(response.data)
        assert response.status_code == 200
        assert b'<form method="post" action="/generate-graph" class="inline">' in response.data
        assert b'<h1>Region: Great Britain</h1>' in response.data
        assert SavedData.query.count() == 1


        
    