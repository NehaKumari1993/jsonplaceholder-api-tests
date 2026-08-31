"""
All coverage for the /photos resource: positive CRUD and negative/edge
cases. Photos are a leaf in the resource graph (see test_albums.py for the
nested /albums/{id}/photos <-> ?albumId= consistency check).
"""
import pytest

from resources import INVALID_ID, RESOURCES_BY_NAME, assert_matches_schema

PHOTOS = RESOURCES_BY_NAME["photos"]


# ---- Positive ----

@pytest.mark.positive
@pytest.mark.smoke
def test_get_all_photos_returns_populated_list(api_session, base_url):
    resp = api_session.get(f"{base_url}/photos")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == PHOTOS["total_count"]
    for item in body:
        assert_matches_schema(item, PHOTOS)
    ids = [item["id"] for item in body]
    assert len(ids) == len(set(ids)), "duplicate ids in the photos list"


@pytest.mark.positive
@pytest.mark.smoke
def test_get_photo_by_id_returns_expected_data(api_session, base_url):
    resp = api_session.get(f"{base_url}/photos/{PHOTOS['valid_id']}")

    assert resp.status_code == 200
    assert resp.json() == PHOTOS["expected_record"]


@pytest.mark.positive
def test_filter_photos_by_album_id(api_session, base_url):
    param_name, param_value = PHOTOS["filter_param"]
    resp = api_session.get(f"{base_url}/photos", params={param_name: param_value})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    for item in body:
        assert_matches_schema(item, PHOTOS)
        assert item[param_name] == param_value


@pytest.mark.positive
def test_create_photo(api_session, base_url):
    resp = api_session.post(f"{base_url}/photos", json=PHOTOS["create_payload"])

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    for key, value in PHOTOS["create_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_replace_photo_with_put(api_session, base_url):
    resp = api_session.put(f"{base_url}/photos/{PHOTOS['valid_id']}", json=PHOTOS["update_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in PHOTOS["update_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_patch_photo_partially_updates(api_session, base_url):
    resp = api_session.patch(f"{base_url}/photos/{PHOTOS['valid_id']}", json=PHOTOS["patch_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in PHOTOS["patch_payload"].items():
        assert body[key] == value
    assert body["id"] == PHOTOS["valid_id"]


@pytest.mark.positive
def test_delete_photo_returns_200(api_session, base_url):
    resp = api_session.delete(f"{base_url}/photos/{PHOTOS['valid_id']}")

    assert resp.status_code == 200


# ---- Negative ----

@pytest.mark.negative
def test_get_photo_by_out_of_range_id_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/photos/{INVALID_ID}")

    assert resp.status_code == 404


@pytest.mark.negative
def test_filter_photos_with_no_matches_returns_empty_list(api_session, base_url):
    param_name, _ = PHOTOS["filter_param"]
    resp = api_session.get(f"{base_url}/photos", params={param_name: INVALID_ID})

    assert resp.status_code == 200
    assert resp.json() == []
