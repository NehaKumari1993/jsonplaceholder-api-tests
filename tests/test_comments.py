"""
All coverage for the /comments resource: positive CRUD and negative/edge
cases. Comments are a leaf in the resource graph (see test_posts.py for the
nested /posts/{id}/comments <-> ?postId= consistency check).
"""
import pytest

from resources import INVALID_ID, RESOURCES_BY_NAME, assert_matches_schema

COMMENTS = RESOURCES_BY_NAME["comments"]


# ---- Positive ----

@pytest.mark.positive
@pytest.mark.smoke
def test_get_all_comments_returns_populated_list(api_session, base_url):
    resp = api_session.get(f"{base_url}/comments")

    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == COMMENTS["total_count"]
    for item in body:
        assert_matches_schema(item, COMMENTS)
    ids = [item["id"] for item in body]
    assert len(ids) == len(set(ids)), "duplicate ids in the comments list"


@pytest.mark.positive
@pytest.mark.smoke
def test_get_comment_by_id_returns_expected_data(api_session, base_url):
    resp = api_session.get(f"{base_url}/comments/{COMMENTS['valid_id']}")

    assert resp.status_code == 200
    assert resp.json() == COMMENTS["expected_record"]


@pytest.mark.positive
def test_filter_comments_by_post_id(api_session, base_url):
    param_name, param_value = COMMENTS["filter_param"]
    resp = api_session.get(f"{base_url}/comments", params={param_name: param_value})

    assert resp.status_code == 200
    body = resp.json()
    assert len(body) > 0
    for item in body:
        assert_matches_schema(item, COMMENTS)
        assert item[param_name] == param_value


@pytest.mark.positive
def test_create_comment(api_session, base_url):
    resp = api_session.post(f"{base_url}/comments", json=COMMENTS["create_payload"])

    assert resp.status_code == 201
    body = resp.json()
    assert "id" in body
    for key, value in COMMENTS["create_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_replace_comment_with_put(api_session, base_url):
    resp = api_session.put(f"{base_url}/comments/{COMMENTS['valid_id']}", json=COMMENTS["update_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in COMMENTS["update_payload"].items():
        assert body[key] == value


@pytest.mark.positive
def test_patch_comment_partially_updates(api_session, base_url):
    resp = api_session.patch(f"{base_url}/comments/{COMMENTS['valid_id']}", json=COMMENTS["patch_payload"])

    assert resp.status_code == 200
    body = resp.json()
    for key, value in COMMENTS["patch_payload"].items():
        assert body[key] == value
    assert body["id"] == COMMENTS["valid_id"]


@pytest.mark.positive
def test_delete_comment_returns_200(api_session, base_url):
    resp = api_session.delete(f"{base_url}/comments/{COMMENTS['valid_id']}")

    assert resp.status_code == 200


# ---- Negative ----

@pytest.mark.negative
def test_get_comment_by_out_of_range_id_returns_404(api_session, base_url):
    resp = api_session.get(f"{base_url}/comments/{INVALID_ID}")

    assert resp.status_code == 404


@pytest.mark.negative
def test_filter_comments_with_no_matches_returns_empty_list(api_session, base_url):
    param_name, _ = COMMENTS["filter_param"]
    resp = api_session.get(f"{base_url}/comments", params={param_name: INVALID_ID})

    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.negative
def test_comment_has_no_real_nested_relation_to_posts(api_session, base_url):
    """
    /comments/{id}/posts looks like a nested route, but comments has no real 
    relation to posts (comments is a leaf resource. Rather than 404 or a 
    filtered result, the fake backend silently returns the full, unfiltered 
    /posts collection, ignoring the comment id entirely.
    """
    resp = api_session.get(f"{base_url}/comments/{COMMENTS['valid_id']}/posts")

    assert resp.status_code == 200
    assert len(resp.json()) == 100  # == plain /posts, not scoped to this comment
