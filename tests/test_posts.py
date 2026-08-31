"""
All coverage for the /posts resource: positive CRUD, negative/edge cases,
and its nested relationship to /comments.

Two miscellaneous, non-posts-specific checks live here too rather than in a
separate file: the unknown-resource-path 404, and the PUT/PATCH/DELETE
nonexistent-id quirks of the fake backend.
"""
import pytest

from resources import INVALID_ID, NONEXISTENT_ID, RESOURCES_BY_NAME, assert_matches_schema

POSTS = RESOURCES_BY_NAME["posts"]


# ---- Positive ----

@pytest.mark.positive
@pytest.mark.smoke
def test_get_all_posts_returns_populated_list(api_session, base_url):
    resp = api_session.get(f"{base_url}/posts")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == POSTS["total_count"]
    for item in body:
        assert_matches_schema(item, POSTS)
    ids = [item["id"] for item in body]
    assert len(ids) == len(set(ids)), "duplicate ids in the posts list"


@pytest.mark.positive
@pytest.mark.smoke
def test_get_post_by_id_returns_expected_data(api_session, base_url):
    resp = api_session.get(f"{base_url}/posts/{POSTS['valid_id']}")

    assert resp.status_code == 200
    assert resp.json() == POSTS["expected_record"]


@pytest.mark.positive
def test_filter_posts_by_user_id(api_session, base_url):
    param_name, param_value = POSTS["filter_param"]
    resp = api_session.get(f"{base_url}/posts", params={param_name: param_value})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    for item in body:
        assert_matches_schema(item, POSTS)
        assert item[param_name] == param_value


@pytest.mark.positive
def test_create_post(api_session, base_url):
    resp = api_session.post(f"{base_url}/posts", json=POSTS["create_payload"])

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    for key, value in POSTS["create_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_replace_post_with_put(api_session, base_url):
    resp = api_session.put(f"{base_url}/posts/{POSTS['valid_id']}", json=POSTS["update_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in POSTS["update_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_patch_post_partially_updates(api_session, base_url):
    resp = api_session.patch(f"{base_url}/posts/{POSTS['valid_id']}", json=POSTS["patch_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in POSTS["patch_payload"].items():
        assert body[key] == value
    # PATCH is partial: fields not in the patch payload should survive untouched.
    assert body["id"] == POSTS["valid_id"]


@pytest.mark.positive
def test_delete_post_returns_200(api_session, base_url):
    resp = api_session.delete(f"{base_url}/posts/{POSTS['valid_id']}")

    assert resp.status_code == 200


# ---- Negative ----

@pytest.mark.negative
def test_get_post_by_out_of_range_id_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/posts/{INVALID_ID}")

    assert resp.status_code == 404


@pytest.mark.negative
def test_get_post_by_non_numeric_id_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/posts/not-a-number")

    assert resp.status_code == 404


@pytest.mark.negative
def test_get_post_by_zero_id_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/posts/0")

    assert resp.status_code == 404


@pytest.mark.negative
def test_filter_posts_with_no_matches_returns_empty_list(api_session, base_url):
    param_name, _ = POSTS["filter_param"]
    resp = api_session.get(f"{base_url}/posts", params={param_name: INVALID_ID})

    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.negative
def test_post_with_empty_body_still_creates(api_session, base_url):
    """The fake API doesn't validate payloads server-side; POST succeeds even with no body."""
    resp = api_session.post(f"{base_url}/posts", json={})

    assert resp.status_code == 201
    assert "id" in resp.json()


@pytest.mark.negative
def test_put_to_nonexistent_post_id_returns_server_error(api_session, base_url):
    """
    Documented quirk: unlike PATCH/DELETE (which fake success on a
    nonexistent id), PUT to a nonexistent id returns 500 on the real API.
    Captured here rather than assumed, since a fake backend doesn't
    guarantee REST-textbook behavior.
    """
    resp = api_session.put(f"{base_url}/posts/{NONEXISTENT_ID}", json={"title": "x"})

    assert resp.status_code == 500


@pytest.mark.negative
def test_patch_to_nonexistent_post_id_fakes_success(api_session, base_url):
    resp = api_session.patch(f"{base_url}/posts/{NONEXISTENT_ID}", json={"title": "x"})

    assert resp.status_code == 200


@pytest.mark.negative
def test_delete_nonexistent_post_id_fakes_success(api_session, base_url):
    resp = api_session.delete(f"{base_url}/posts/{NONEXISTENT_ID}")

    assert resp.status_code == 200


@pytest.mark.negative
def test_get_unknown_resource_path_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/not-a-real-resource")

    assert resp.status_code == 404


# ---- Nested ----

@pytest.mark.nested
def test_post_comments_nested_route(api_session, base_url):
    resp = api_session.get(f"{base_url}/posts/{POSTS['valid_id']}/comments")

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    assert all(comment["postId"] == POSTS["valid_id"] for comment in body)


@pytest.mark.nested
def test_post_comments_nested_route_matches_filter_query(api_session, base_url):
    nested = api_session.get(f"{base_url}/posts/{POSTS['valid_id']}/comments").json()
    filtered = api_session.get(f"{base_url}/comments", params={"postId": POSTS["valid_id"]}).json()

    assert {c["id"] for c in nested} == {c["id"] for c in filtered}
