"""User profile tests."""

import pytest


@pytest.mark.asyncio
async def test_change_password_flow(client):
    # Register + login
    await client.post("/api/v1/auth/register", json={
        "username": "carol", "email": "carol@example.com",
        "password": "OldPass1234!@#", "password_confirm": "OldPass1234!@#",
    })
    r = await client.post("/api/v1/auth/login", json={
        "identifier": "carol@example.com", "password": "OldPass1234!@#",
    })
    access = r.json()["data"]["access_token"]

    # Change password
    r = await client.post("/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {access}"},
        json={"current_password": "OldPass1234!@#",
              "new_password": "NewPass1234!@#",
              "new_password_confirm": "NewPass1234!@#"})
    assert r.status_code == 200

    # Old token now invalid (sessions were revoked)
    r = await client.get("/api/v1/users/me",
                         headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 401

    # New password works
    r = await client.post("/api/v1/auth/login", json={
        "identifier": "carol@example.com", "password": "NewPass1234!@#",
    })
    assert r.status_code == 200