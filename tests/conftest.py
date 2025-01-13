

import os
import sys
# Add the project root to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pytest
from app import create_app

@pytest.fixture
def app():
    # setup code
    app = create_app()
    yield app  # return the app instance

@pytest.fixture
def client(app): # app is the fixture name
    return app.test_client()