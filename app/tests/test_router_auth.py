"""
Every router except products used to be reachable with no token at all.
All routers now require get_current_user, so every one of them should
reject an unauthenticated request the same way.
"""
import pytest


@pytest.mark.parametrize(
    "method, path",
    [
        ("get", "/products/"),
        ("get", "/users/"),
        ("post", "/users/"),
        ("get", "/customers/"),
        ("get", "/sales/"),
        ("post", "/sales/"),
        ("get", "/payments/"),
        ("get", "/suppliers/"),
        ("delete", "/suppliers/1"),
        ("get", "/inventory/"),
        ("get", "/receipts/"),
        ("get", "/sale-items/"),
    ],
)
def test_endpoints_reject_unauthenticated_requests(client, method, path):
    if method == "post":
        response = client.post(path, json={})
    else:
        response = getattr(client, method)(path)
    assert response.status_code == 401
