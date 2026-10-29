import os
import sys
import tempfile
import pytest

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from secureshop import create_app
from secureshop.config import SecureConfig, VulnerableConfig
from secureshop.seed import seed_database
from secureshop.database import init_db

class TestSecureConfig(SecureConfig):
    TESTING = True
    WTF_CSRF_ENABLED = True
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 900

class TestVulnerableConfig(VulnerableConfig):
    TESTING = True
    MAX_LOGIN_ATTEMPTS = 999999
    ENABLE_CSRF = False

@pytest.fixture
def secure_app():
    """Create and configure a clean instance of SecureShop in SECURE mode with a temporary database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    log_fd, log_path = tempfile.mkstemp(suffix=".log")
    os.close(log_fd)
    os.environ["SECURITY_LOG_PATH"] = log_path

    config = TestSecureConfig()
    config.DATABASE_PATH = db_path

    seed_database(db_path)
    app = create_app(config)

    yield app

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
        except OSError:
            pass

@pytest.fixture
def secure_client(secure_app):
    """Test client for secure app."""
    return secure_app.test_client()

@pytest.fixture
def vulnerable_app():
    """Create and configure a clean instance of SecureShop in VULNERABLE mode with a temporary database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)

    log_fd, log_path = tempfile.mkstemp(suffix=".log")
    os.close(log_fd)
    os.environ["SECURITY_LOG_PATH"] = log_path

    config = TestVulnerableConfig()
    config.DATABASE_PATH = db_path

    seed_database(db_path)
    app = create_app(config)

    yield app

    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass
    if os.path.exists(log_path):
        try:
            os.remove(log_path)
        except OSError:
            pass

@pytest.fixture
def vulnerable_client(vulnerable_app):
    """Test client for vulnerable lab app."""
    return vulnerable_app.test_client()

def get_csrf_token(client):
    """Retrieve active session CSRF token."""
    with client.session_transaction() as sess:
        return sess.get("csrf_token")

def login(client, username, password):
    """Helper to perform authenticated sign in."""
    client.get("/login")
    token = get_csrf_token(client)
    data = {
        "username": username,
        "password": password
    }
    if token:
        data["csrf_token"] = token
    return client.post("/login", data=data, follow_redirects=True)
