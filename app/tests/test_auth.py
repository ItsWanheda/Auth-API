"""Authentication flow integration tests."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_register_login_refresh_logout(client):
    # Register
    r = await client.post("/api/v1/auth/register", json={
        "username": "alice", "email": "alice@example.com",
        "full_name": "Alice", "password": "Sup3r$trongPass!",
        "password_confirm": "Sup3r$trongPass!",
    })
    assert r.status_code == 201, r.text
    assert r.json()["success"] is True
    assert r.json()["data"]["email"] == "alice@example.com"

    # Duplicate registration → 409
    r2 = await client.post("/api/v1/auth/register", json={
        "username": "alice", "email": "alice@example.com",
        "password": "Sup3r$trongPass!", "password_confirm": "Sup3r$trongPass!",
    })
    assert r2.status_code == 409

    # Login
    r = await client.post("/api/v1/auth/login", json={
        "identifier": "alice@example.com", "password": "Sup3r$trongPass!",
    })
    assert r.status_code == 200, r.text
    body = r.json()["data"]
    access, refresh = body["access_token"], body["refresh_token"]
    assert body["token_type"] == "bearer"

    # /users/me with the access token
    r = await client.get("/api/v1/users/me",
                         headers={"Authorization": f"Bearer {access}"})
    assert r.status_code == 200
    assert r.json()["data"]["username"] == "alice"

    # Rotate refresh token
    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 200
    new_refresh = r.json()["data"]["refresh_token"]
    assert new_refresh != refresh

    # Reusing the OLD refresh token should fail.
    r = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert r.status_code == 401

    # Logout
    r = await client.post("/api/v1/auth/logout", json={"refresh_token": new_refresh})
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_login_bad_password(client):
    await client.post("/api/v1/auth/register", json={
        "username": "bob", "email": "bob@example.com",
        "password": "Sup3r$trongPass!", "password_confirm": "Sup3r$trongPass!",
    })
    r = await client.post("/api/v1/auth/login", json={
        "identifier": "bob@example.com", "password": "WrongPass1!",
    })
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_protected_endpoint_without_token(client):
    r = await client.get("/api/v1/users/me")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_health(client):
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"