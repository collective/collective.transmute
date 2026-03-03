from collective.transmute.utils import exportimport
from typing import Any

import pytest


@pytest.fixture
def src_data(load_json_resource):
    return load_json_resource("export_localroles.json")


@pytest.mark.parametrize(
    "uuid,key,expected",
    [
        ("a7f39c2b59c040d0ada279702ce2bd5a", "block", None),
        ("a7f39c2b59c040d0ada279702ce2bd5a", "local_roles", {"site": ["Owner"]}),
        ("bee76beb1f234d7c9797ff3acb530299", "block", 1),
        ("bee76beb1f234d7c9797ff3acb530299", "local_roles", {}),
    ],
)
def test__initialize_localroles(src_data, uuid: str, key: str, expected: Any):
    result = exportimport._initialize_localroles(src_data)
    entry = result.get(uuid)
    assert entry is not None, f"Entry for uuid {uuid} not found in result"
    assert entry.get(key) == expected
