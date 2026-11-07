import pytest


@pytest.mark.asyncio
async def test_create_business(client):
    response = await client.post(
        "/api/v1/businesses",
        json={
            "legal_name": "Olaynex Test Limited",
            "display_name": "Olaynex Test",
            "country_code": "NG",
            "base_currency": "NGN",
            "email": "test@example.com",
            "phone": "+2348000000000",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["legal_name"] == "Olaynex Test Limited"
    assert data["display_name"] == "Olaynex Test"
    assert data["country_code"] == "NG"
    assert data["base_currency"] == "NGN"
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_list_businesses(client):
    await client.post(
        "/api/v1/businesses",
        json={
            "legal_name": "Business One Limited",
            "country_code": "NG",
            "base_currency": "NGN",
        },
    )

    await client.post(
        "/api/v1/businesses",
        json={
            "legal_name": "Business Two Limited",
            "country_code": "US",
            "base_currency": "USD",
        },
    )

    response = await client.get("/api/v1/businesses")

    assert response.status_code == 200

    businesses = response.json()

    assert len(businesses) == 2
    assert {
        business["legal_name"] for business in businesses
    } == {
        "Business One Limited",
        "Business Two Limited",
    }


@pytest.mark.asyncio
async def test_get_business_by_id(client):
    create_response = await client.post(
        "/api/v1/businesses",
        json={
            "legal_name": "Retrieval Test Limited",
            "country_code": "NG",
            "base_currency": "NGN",
        },
    )

    business_id = create_response.json()["id"]

    response = await client.get(
        f"/api/v1/businesses/{business_id}"
    )

    assert response.status_code == 200
    assert response.json()["id"] == business_id
    assert response.json()["legal_name"] == "Retrieval Test Limited"


@pytest.mark.asyncio
async def test_get_nonexistent_business_returns_404(client):
    response = await client.get(
        "/api/v1/businesses/00000000-0000-0000-0000-000000000001"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Business not found"
