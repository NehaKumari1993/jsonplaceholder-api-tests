"""
Central config table describing each JSONPlaceholder resource: ids, the
exact known record at each valid_id, and request payloads. Each
test_<resource>.py file looks up its own entry here by name instead of
hardcoding those values inline.
"""

RESOURCES = [
    {
        # userId 3 verified via GET /posts/23
        "name": "posts",
        "valid_id": 23,
        "total_count": 100,
        "expected_record": {
            "userId": 3,
            "id": 23,
            "title": "maxime id vitae nihil numquam",
            "body": "veritatis unde neque eligendi\nquae quod architecto quo neque vitae\n"
                     "est illo sit tempora doloremque fugit quod\n"
                     "et et vel beatae sequi ullam sed tenetur perspiciatis",
        },
        "create_payload": {"title": "foo", "body": "bar", "userId": 3},
        "update_payload": {"id": 23, "title": "updated title", "body": "updated body", "userId": 3},
        "patch_payload": {"title": "patched title"},
        "filter_param": ("userId", 3),
    },
    {
        # postId 18 verified via GET /comments/87
        "name": "comments",
        "valid_id": 87,
        "total_count": 500,
        "expected_record": {
            "postId": 18,
            "id": 87,
            "name": "dolor asperiores autem et omnis quasi nobis",
            "email": "Grover_Volkman@coty.tv",
            "body": "assumenda corporis architecto repudiandae omnis qui et odit\n"
                     "perferendis velit enim\net quia reiciendis sint\n"
                     "quia voluptas quam deserunt facilis harum eligendi",
        },
        "create_payload": {"postId": 18, "name": "test name", "email": "test@example.com", "body": "test body"},
        "update_payload": {"postId": 18, "id": 87, "name": "updated", "email": "updated@example.com", "body": "updated body"},
        "patch_payload": {"name": "patched name"},
        "filter_param": ("postId", 18),
    },
    {
        # userId 5 verified via GET /albums/42
        "name": "albums",
        "valid_id": 42,
        "total_count": 100,
        "expected_record": {"userId": 5, "id": 42, "title": "tenetur explicabo ea"},
        "create_payload": {"userId": 5, "title": "test album"},
        "update_payload": {"userId": 5, "id": 42, "title": "updated album"},
        "patch_payload": {"title": "patched album"},
        "filter_param": ("userId", 5),
    },
    {
        # albumId 25 verified via GET /photos/1234
        "name": "photos",
        "valid_id": 1234,
        "total_count": 5000,
        "expected_record": {
            "albumId": 25,
            "id": 1234,
            "title": "voluptas ipsum officiis architecto quos tenetur",
            "url": "https://via.placeholder.com/600/2fb4ba",
            "thumbnailUrl": "https://via.placeholder.com/150/2fb4ba",
        },
        "create_payload": {
            "albumId": 25,
            "title": "test photo",
            "url": "https://via.placeholder.com/600",
            "thumbnailUrl": "https://via.placeholder.com/150",
        },
        "update_payload": {
            "albumId": 25,
            "id": 1234,
            "title": "updated photo",
            "url": "https://via.placeholder.com/600",
            "thumbnailUrl": "https://via.placeholder.com/150",
        },
        "patch_payload": {"title": "patched photo"},
        "filter_param": ("albumId", 25),
    },
    {
        # userId 8 verified via GET /todos/150
        "name": "todos",
        "valid_id": 150,
        "total_count": 200,
        "expected_record": {
            "userId": 8,
            "id": 150,
            "title": "eos amet tempore laudantium fugit a",
            "completed": False,
        },
        "create_payload": {"userId": 8, "title": "test todo", "completed": False},
        "update_payload": {"userId": 8, "id": 150, "title": "updated todo", "completed": True},
        "patch_payload": {"completed": True},
        "filter_param": ("userId", 8),
    },
    {
        # username "Karianne" verified via GET /users/4
        "name": "users",
        "valid_id": 4,
        "total_count": 10,
        "expected_record": {
            "id": 4,
            "name": "Patricia Lebsack",
            "username": "Karianne",
            "email": "Julianne.OConner@kory.org",
            "address": {
                "street": "Hoeger Mall",
                "suite": "Apt. 692",
                "city": "South Elvis",
                "zipcode": "53919-4257",
                "geo": {"lat": "29.4572", "lng": "-164.2990"},
            },
            "phone": "493-170-9623 x156",
            "website": "kale.biz",
            "company": {
                "name": "Robel-Corkery",
                "catchPhrase": "Multi-tiered zero tolerance productivity",
                "bs": "transition cutting-edge web services",
            },
        },
        "create_payload": {"name": "Test User", "username": "testuser", "email": "test@example.com"},
        "update_payload": {"id": 4, "name": "Updated User", "username": "updateduser", "email": "updated@example.com"},
        "patch_payload": {"name": "Patched User"},
        "filter_param": ("username", "Karianne"),
    },
]

RESOURCES_BY_NAME = {r["name"]: r for r in RESOURCES}

INVALID_ID = 999999
NONEXISTENT_ID = 999  # inside the fake API's "doesn't really exist" range for most resources


def assert_matches_schema(item, resource):
    """
    Checks that item has every field present on the resource's known
    expected_record. Used against list/filter results, where there's no
    single known record to match exactly, so a field silently missing on
    any one item still fails the test.
    """
    required_fields = resource["expected_record"].keys()
    missing = required_fields - item.keys()
    assert not missing, f"{resource['name']} item {item.get('id')} is missing fields: {missing}"
