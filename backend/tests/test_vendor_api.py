import pytest


async def create_business(client, legal_name):
    response = await client.post(
        "/api/v1/businesses",
        json={
            "legal_name": legal_name,
            "country_code": "NG",
            "base_currency": "NGN",
        },
    )

    assert response.status_code == 201
    return response.json()


async def create_vendor(client, business_id, name="Test Vendor"):
    response = await client.post(
        f"/api/v1/businesses/{business_id}/vendors",
        json={
            "name": name,
            "email": "vendor@example.com",
            "country_code": "US",
            "preferred_currency": "USD",
            "payment_method": "bank_transfer",
            "notes": "Initial vendor notes",
        },
    )

    assert response.status_code == 201
    return response.json()


@pytest.mark.asyncio
async def test_create_vendor_under_business(client):
    business = await create_business(client, "Vendor Owner Limited")

    response = await client.post(
        f"/api/v1/businesses/{business['id']}/vendors",
        json={
            "name": "Acme Supplies",
            "email": "acme@example.com",
            "country_code": "US",
            "preferred_currency": "USD",
            "payment_method": "bank_transfer",
            "notes": "Office equipment supplier",
        },
    )

    assert response.status_code == 201

    vendor = response.json()

    assert vendor["name"] == "Acme Supplies"
    assert vendor["business_id"] == business["id"]
    assert vendor["country_code"] == "US"
    assert vendor["preferred_currency"] == "USD"
    assert vendor["is_active"] is True
    assert "id" in vendor


@pytest.mark.asyncio
async def test_list_vendors_only_returns_business_vendors(client):
    business_a = await create_business(client, "Business A Limited")
    business_b = await create_business(client, "Business B Limited")

    vendor_a = await create_vendor(
        client,
        business_a["id"],
        "Vendor A",
    )

    await create_vendor(
        client,
        business_b["id"],
        "Vendor B",
    )

    response = await client.get(
        f"/api/v1/businesses/{business_a['id']}/vendors"
    )

    assert response.status_code == 200

    vendors = response.json()

    assert len(vendors) == 1
    assert vendors[0]["id"] == vendor_a["id"]
    assert vendors[0]["business_id"] == business_a["id"]


@pytest.mark.asyncio
async def test_update_vendor_preserves_omitted_fields(client):
    business = await create_business(client, "Update Test Limited")
    vendor = await create_vendor(client, business["id"])

    response = await client.patch(
        f"/api/v1/businesses/{business['id']}/vendors/{vendor['id']}",
        json={
            "preferred_currency": "EUR",
            "notes": "Updated payment currency",
        },
    )

    assert response.status_code == 200

    updated_vendor = response.json()

    assert updated_vendor["preferred_currency"] == "EUR"
    assert updated_vendor["notes"] == "Updated payment currency"

    # These fields were omitted from the PATCH request.
    assert updated_vendor["name"] == "Test Vendor"
    assert updated_vendor["email"] == "vendor@example.com"
    assert updated_vendor["country_code"] == "US"
    assert updated_vendor["payment_method"] == "bank_transfer"


@pytest.mark.asyncio
async def test_create_vendor_for_nonexistent_business_returns_404(client):
    response = await client.post(
        "/api/v1/businesses/00000000-0000-0000-0000-000000000001/vendors",
        json={
            "name": "Orphan Vendor",
            "country_code": "US",
            "preferred_currency": "USD",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Business not found"


@pytest.mark.asyncio
async def test_list_vendors_for_nonexistent_business_returns_404(client):
    response = await client.get(
        "/api/v1/businesses/00000000-0000-0000-0000-000000000001/vendors"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Business not found"


@pytest.mark.asyncio
async def test_update_nonexistent_vendor_returns_404(client):
    business = await create_business(client, "Vendor Lookup Limited")

    response = await client.patch(
        f"/api/v1/businesses/{business['id']}/vendors/"
        "00000000-0000-0000-0000-000000000001",
        json={"notes": "This vendor does not exist"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found"


@pytest.mark.asyncio
async def test_business_cannot_list_another_business_vendors(client):
    business_a = await create_business(client, "Owner Business Limited")
    business_b = await create_business(client, "Other Business Limited")

    vendor_a = await create_vendor(
        client,
        business_a["id"],
        "Private Vendor A",
    )

    response = await client.get(
        f"/api/v1/businesses/{business_b['id']}/vendors"
    )

    assert response.status_code == 200
    assert response.json() == []
    assert vendor_a["id"] not in {
        vendor["id"] for vendor in response.json()
    }


@pytest.mark.asyncio
async def test_business_cannot_update_another_business_vendor(client):
    business_a = await create_business(client, "Vendor Owner Limited")
    business_b = await create_business(client, "Unauthorized Business Limited")

    vendor_a = await create_vendor(
        client,
        business_a["id"],
        "Protected Vendor",
    )

    response = await client.patch(
        f"/api/v1/businesses/{business_b['id']}/vendors/{vendor_a['id']}",
        json={
            "name": "Unauthorized Modification",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Vendor not found"

    # Verify the original vendor remains unchanged.
    owner_response = await client.get(
        f"/api/v1/businesses/{business_a['id']}/vendors"
    )

    assert owner_response.status_code == 200
    assert owner_response.json()[0]["name"] == "Protected Vendor"
