from main.database import SavedData
from .helper_functions_for_testing import create_a_response
from .database_fixture import client, main_app


def test_request(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Search Parameter" in response.data


def test_search_without_selecting_markets(client, main_app):
    with main_app.app_context():

        response = create_a_response(client=client,
                                     url="/",
                                     search_parameter="epiphone electric guitar",
                                     delivery_destination="LT")

        assert b'action="/generate-graph"' in response.data
        assert response.status_code == 200
        assert SavedData.query.count() == 1


def test_search_with_market(client, main_app):
    with main_app.app_context():

        response = create_a_response(client=client, url="/",
                                     search_parameter="epiphone electric guitar",
                                     market="['EBAY_GB', 'GBP']",
                                     delivery_destination="LT")

        assert response.status_code == 200
        assert b'action="/generate-graph"' in response.data
        assert b'<h1>Region: Great Britain</h1>' in response.data
        assert SavedData.query.count() == 1


def test_search_with_several_markets(client, main_app):
    with main_app.app_context():
        response = create_a_response(client=client, url="/",
                                     search_parameter="iphone 16 smartphone",
                                     market=["['EBAY_DE', 'EUR']",
                                             "['EBAY_US', 'USD']"],
                                     delivery_destination="LT")

        assert response.status_code == 200
        assert b'action="/generate-graph' in response.data
        assert b'<h1>Region: Germany</h1>' in response.data
        assert b'<h1>Region: USA</h1>' in response.data
        assert SavedData.query.count() == 1


def test_about_page(client, main_app):
    with main_app.app_context():
        response = client.get("/about")

        assert response.status_code == 200
