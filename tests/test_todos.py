"""
All coverage for the /todos resource: positive CRUD and negative/edge cases.
Todos are a leaf in the resource graph (see test_users.py for the nested
/users/{id}/todos route).
"""
import pytest

from resources import INVALID_ID, RESOURCES_BY_NAME, assert_matches_schema

TODOS = RESOURCES_BY_NAME["todos"]


# ---- Positive ----

@pytest.mark.positive
@pytest.mark.smoke
def test_get_all_todos_returns_populated_list(api_session, base_url):
    resp = api_session.get(f"{base_url}/todos")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == TODOS["total_count"]
    for item in body:
        assert_matches_schema(item, TODOS)
    ids = [item["id"] for item in body]
    assert len(ids) == len(set(ids)), "duplicate ids in the todos list"


@pytest.mark.positive
@pytest.mark.smoke
def test_get_todo_by_id_returns_expected_data(api_session, base_url):
    resp = api_session.get(f"{base_url}/todos/{TODOS['valid_id']}")

    assert resp.status_code == 200
    assert resp.json() == TODOS["expected_record"]


@pytest.mark.positive
def test_filter_todos_by_user_id(api_session, base_url):
    param_name, param_value = TODOS["filter_param"]
    resp = api_session.get(f"{base_url}/todos", params={param_name: param_value})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    for item in body:
        assert_matches_schema(item, TODOS)
        assert item[param_name] == param_value


@pytest.mark.positive
def test_create_todo(api_session, base_url):
    resp = api_session.post(f"{base_url}/todos", json=TODOS["create_payload"])

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    for key, value in TODOS["create_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_replace_todo_with_put(api_session, base_url):
    resp = api_session.put(f"{base_url}/todos/{TODOS['valid_id']}", json=TODOS["update_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in TODOS["update_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_patch_todo_partially_updates(api_session, base_url):
    resp = api_session.patch(f"{base_url}/todos/{TODOS['valid_id']}", json=TODOS["patch_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in TODOS["patch_payload"].items():
        assert body[key] == value
    assert body["id"] == TODOS["valid_id"]


@pytest.mark.positive
def test_delete_todo_returns_200(api_session, base_url):
    resp = api_session.delete(f"{base_url}/todos/{TODOS['valid_id']}")

    assert resp.status_code == 200


# ---- Negative ----

@pytest.mark.negative
def test_get_todo_by_out_of_range_id_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/todos/{INVALID_ID}")

    assert resp.status_code == 404


@pytest.mark.negative
def test_filter_todos_with_no_matches_returns_empty_list(api_session, base_url):
    param_name, _ = TODOS["filter_param"]
    resp = api_session.get(f"{base_url}/todos", params={param_name: INVALID_ID})

    assert resp.status_code == 200
    assert resp.json() == []
