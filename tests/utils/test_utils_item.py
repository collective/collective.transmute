from collective.transmute.utils import item

import pytest


@pytest.mark.parametrize(
    "id_,expected",
    [
        ["/path", set()],
        ["/path/subpath", {"/path", "/path/"}],
        [
            "/path/subpath/first_child",
            {"/path", "/path/", "/path/subpath", "/path/subpath/"},
        ],
        [
            "/path/subpath/second_child",
            {"/path", "/path/", "/path/subpath", "/path/subpath/"},
        ],
    ],
)
def test_all_parents_for(id_: str, expected: set):
    func = item.all_parents_for
    assert func(id_) == expected
