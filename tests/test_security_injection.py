def test_sqli_defense_in_secure_mode(secure_client):
    """A03 Defense: Verify parameterized SQL query handles injection attempts safely without logic bypass."""
    # Classic boolean SQL injection payload
    payload = "' OR '1'='1"
    res = secure_client.get(f"/search?q={payload}")
    assert res.status_code == 200

    # In secure mode, the input is parameterized literally:
    # No products have the literal string "' OR '1'='1" in their name, so empty state is displayed
    assert b"No Products Found" in res.data
    assert b"Showing 0 active items" in res.data

def test_sqli_vulnerability_demonstrated_in_lab_mode(vulnerable_client):
    """A03 Vulnerability: Demonstrate that unparameterized string concatenation allows query alteration in lab mode."""
    # When vulnerable, payload ' OR '1'='1' closes the LIKE quote and injects a tautology
    # Note: SQLite syntax for LIKE concatenation: '% ' OR '1'='1 %'
    payload = "' OR 1=1 --"
    res = vulnerable_client.get(f"/search?q={payload}")
    assert res.status_code == 200

    # The query condition was bypassed via injection, returning catalog items
    assert b"Hardware Security Key Pro" in res.data
    assert b"Hardware Crypto Cold Storage" in res.data

def test_sqli_syntax_error_handling_in_secure_mode(secure_client):
    """A03 Defense: Verify unmatched single quotes do not trigger database syntax errors in secure mode."""
    res = secure_client.get("/search?q='")
    assert res.status_code == 200
    assert b"No Products Found" in res.data
