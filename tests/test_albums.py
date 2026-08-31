"""
All coverage for the /albums resource: positive CRUD, negative/edge cases,
and its nested relationship to /photos.
"""
import pytest

from resources import INVALID_ID, RESOURCES_BY_NAME, assert_matches_schema

ALBUMS = RESOURCES_BY_NAME["albums"]


# ---- Positive ----

@pytest.mark.positive
@pytest.mark.smoke
def test_get_all_albums_returns_populated_list(api_session, base_url):
    resp = api_session.get(f"{base_url}/albums")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == ALBUMS["total_count"]
    for item in body:
        assert_matches_schema(item, ALBUMS)
    ids = [item["id"] for item in body]
    assert len(ids) == len(set(ids)), "duplicate ids in the albums list"


@pytest.mark.positive
@pytest.mark.smoke
def test_get_album_by_id_returns_expected_data(api_session, base_url):
    resp = api_session.get(f"{base_url}/albums/{ALBUMS['valid_id']}")

    assert resp.status_code == 200
    assert resp.json() == ALBUMS["expected_record"]


@pytest.mark.positive
def test_filter_albums_by_user_id(api_session, base_url):
    param_name, param_value = ALBUMS["filter_param"]
    resp = api_session.get(f"{base_url}/albums", params={param_name: param_value})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    for item in body:
        assert_matches_schema(item, ALBUMS)
        assert item[param_name] == param_value


@pytest.mark.positive
def test_create_album(api_session, base_url):
    resp = api_session.post(f"{base_url}/albums", json=ALBUMS["create_payload"])

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    for key, value in ALBUMS["create_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_replace_album_with_put(api_session, base_url):
    resp = api_session.put(f"{base_url}/albums/{ALBUMS['valid_id']}", json=ALBUMS["update_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in ALBUMS["update_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_patch_album_partially_updates(api_session, base_url):
    resp = api_session.patch(f"{base_url}/albums/{ALBUMS['valid_id']}", json=ALBUMS["patch_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in ALBUMS["patch_payload"].items():
        assert body[key] == value
    assert body["id"] == ALBUMS["valid_id"]


@pytest.mark.positive
def test_delete_album_returns_200(api_session, base_url):
    resp = api_session.delete(f"{base_url}/albums/{ALBUMS['valid_id']}")

    assert resp.status_code == 200


# ---- Negative ----

@pytest.mark.negative
def test_get_album_by_out_of_range_id_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/albums/{INVALID_ID}")

    assert resp.status_code == 404


@pytest.mark.negative
def test_filter_albums_with_no_matches_returns_empty_list(api_session, base_url):
    param_name, _ = ALBUMS["filter_param"]
    resp = api_session.get(f"{base_url}/albums", params={param_name: INVALID_ID})

    assert resp.status_code == 200
    assert resp.json() == []


# ---- Nested ----

@pytest.mark.nested
def test_album_photos_nested_route(api_session, base_url):
    resp = api_session.get(f"{base_url}/albums/{ALBUMS['valid_id']}/photos")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    assert all(photo["albumId"] == ALBUMS["valid_id"] for photo in body)


@pytest.mark.nested
def test_album_photos_nested_route_matches_filter_query(api_session, base_url):
    nested = api_session.get(f"{base_url}/albums/{ALBUMS['valid_id']}/photos").json()
    filtered = api_session.get(f"{base_url}/photos", params={"albumId": ALBUMS["valid_id"]}).json()

    assert {p["id"] for p in nested} == {p["id"] for p in filtered}
