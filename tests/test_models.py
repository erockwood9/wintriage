import json

from wintriage.models import Status


def test_status_serializes_as_plain_text():
    assert json.dumps(Status.OK) == '"ok"'
