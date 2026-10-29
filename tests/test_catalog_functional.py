def test_catalog_index_and_listing(secure_client):
    """Test public home page and catalog list display."""
    res = secure_client.get("/")
    assert res.status_code == 200
    assert b"SecureShop" in res.data
    assert b"Featured Equipment" in res.data

    cat_res = secure_client.get("/catalog")
    assert cat_res.status_code == 200
    assert b"Hardware Security Key Pro" in cat_res.data
    assert b"Hardware Crypto Cold Storage" in cat_res.data

def test_catalog_category_filter(secure_client):
    """Test filtering catalog by specific product category."""
    res = secure_client.get("/catalog?category=Books")
    assert res.status_code == 200
    assert b"Web Application Security Handbook" in res.data
    # Other categories should not show
    assert b"ANC Wireless Studio Headphones" not in res.data

def test_catalog_sorting(secure_client):
    """Test sorting products by price ascending."""
    res = secure_client.get("/catalog?sort=price_asc")
    assert res.status_code == 200
    assert b"USB-C Data Blocker Connector" in res.data

def test_product_detail_view(secure_client):
    """Test viewing an individual active product detail page."""
    res = secure_client.get("/products/1")
    assert res.status_code == 200
    assert b"Hardware Security Key Pro" in res.data
    assert b"FIDO2" in res.data
    assert b"Add to Cart" in res.data

def test_product_detail_not_found(secure_client):
    """Test requesting a non-existent or inactive product."""
    res = secure_client.get("/products/99999")
    assert res.status_code == 404

    # Product 11 is inactive internal prototype
    inactive_res = secure_client.get("/products/11")
    assert inactive_res.status_code == 404

def test_search_valid_query(secure_client):
    """Test searching for products with keyword match."""
    res = secure_client.get("/search?q=Key")
    assert res.status_code == 200
    assert b"Hardware Security Key Pro" in res.data
    assert b"Mechanical Developer Keyboard" in res.data

def test_search_empty_results(secure_client):
    """Test searching for non-matching keyword shows empty state."""
    res = secure_client.get("/search?q=NonExistentKeywordXYZ")
    assert res.status_code == 200
    assert b"No Products Found" in res.data
