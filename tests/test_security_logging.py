import os
from tests.conftest import login, get_csrf_token

def test_security_logging_on_auth_failure_and_idor(secure_client):
    """A09 Defense: Verify security events are logged to database without exposing secrets."""
    # 1. Trigger failed login with password attempt
    login(secure_client, "alice", "SecretPasswordAttempt999!")

    # 2. Trigger IDOR denial
    login(secure_client, "alice", "AlicePass123!")
    secure_client.get("/orders/3")  # Bob's order

    # Inspect logged events in database
    with secure_client.application.app_context():
        from secureshop.database import query_db
        events = query_db("SELECT * FROM security_events ORDER BY id DESC")
        event_types = [e["event_type"] for e in events]

        assert "AUTH_FAILURE" in event_types
        assert "AUTHZ_DENIED_IDOR" in event_types

        # Verify sensitive password was scrubbed / redacted
        for e in events:
            details_str = e["details"]
            assert "SecretPasswordAttempt999!" not in details_str
            assert "AlicePass123!" not in details_str
