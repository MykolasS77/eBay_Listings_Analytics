import pytest
from main import create_app, db
from main.database import SavedData
from .helper_functions_for_testing import create_a_response
import json
import os


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
