"""
All coverage for the /users resource: positive CRUD, negative/edge cases,
and its nested relationships to /posts, /albums, and /todos (users is the
root of the resource graph).
"""
import pytest

from resources import INVALID_ID, RESOURCES_BY_NAME, assert_matches_schema

USERS = RESOURCES_BY_NAME["users"]


# ---- Positive ----

@pytest.mark.positive
@pytest.mark.smoke
def test_get_all_users_returns_populated_list(api_session, base_url):
    resp = api_session.get(f"{base_url}/users")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == USERS["total_count"]
    for item in body:
        assert_matches_schema(item, USERS)
    ids = [item["id"] for item in body]
    assert len(ids) == len(set(ids)), "duplicate ids in the users list"


@pytest.mark.positive
@pytest.mark.smoke
def test_get_user_by_id_returns_expected_data(api_session, base_url):
    """Exact-value match, including the nested address/geo/company objects."""
    resp = api_session.get(f"{base_url}/users/{USERS['valid_id']}")

    assert resp.status_code == 200
    assert resp.json() == USERS["expected_record"]


@pytest.mark.positive
def test_filter_users_by_username(api_session, base_url):
    param_name, param_value = USERS["filter_param"]
    resp = api_session.get(f"{base_url}/users", params={param_name: param_value})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0] == USERS["expected_record"]


@pytest.mark.positive
def test_create_user(api_session, base_url):
    resp = api_session.post(f"{base_url}/users", json=USERS["create_payload"])

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    for key, value in USERS["create_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_replace_user_with_put(api_session, base_url):
    resp = api_session.put(f"{base_url}/users/{USERS['valid_id']}", json=USERS["update_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in USERS["update_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_patch_user_partially_updates(api_session, base_url):
    resp = api_session.patch(f"{base_url}/users/{USERS['valid_id']}", json=USERS["patch_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in USERS["patch_payload"].items():
        assert body[key] == value
    assert body["id"] == USERS["valid_id"]


@pytest.mark.positive
def test_delete_user_returns_200(api_session, base_url):
    resp = api_session.delete(f"{base_url}/users/{USERS['valid_id']}")

    assert resp.status_code == 200


# ---- Negative ----

@pytest.mark.negative
def test_get_user_by_out_of_range_id_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/users/{INVALID_ID}")

    assert resp.status_code == 404


@pytest.mark.negative
def test_filter_users_with_no_matching_username_returns_empty_list(api_session, base_url):
    resp = api_session.get(f"{base_url}/users", params={"username": "no-such-user"})

    assert resp.status_code == 200
    assert resp.json() == []


# ---- Nested ----

@pytest.mark.nested
@pytest.mark.parametrize("nested_path", ["posts", "albums", "todos"])
def test_user_nested_routes(api_session, base_url, nested_path):
    resp = api_session.get(f"{base_url}/users/{USERS['valid_id']}/{nested_path}")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    assert all(item["userId"] == USERS["valid_id"] for item in body)


@pytest.mark.nested
@pytest.mark.parametrize("nested_path,filter_key", [("posts", "userId"), ("albums", "userId"), ("todos", "userId")])
def test_user_nested_routes_match_filter_query(api_session, base_url, nested_path, filter_key):
    nested = api_session.get(f"{base_url}/users/{USERS['valid_id']}/{nested_path}").json()
    filtered = api_session.get(f"{base_url}/{nested_path}", params={filter_key: USERS["valid_id"]}).json()

    assert {item["id"] for item in nested} == {item["id"] for item in filtered}
