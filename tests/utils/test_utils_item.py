from collective.transmute import _types as t
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


@pytest.mark.parametrize(
    "parent,expected",
    [
        (
            {
                "@id": "/parent",
                "id": "parent",
                "@type": "News Item",
                "title": "Parent Item",
                "image": {
                    "filename": "sample-image.jpg",
                    "data": b"image-data",
                },
                "image_caption": "An example image.",
            },
            {
                "@id": "/parent/sample-image.jpg",
                "@type": "Image",
                "id": "sample-image.jpg",
                "title": "sample-image.jpg",
                "image": {
                    "filename": "sample-image.jpg",
                    "data": b"image-data",
                },
                "image_caption": "An example image.",
            },
        ),
        (
            {
                "@id": "/parent",
                "id": "parent",
                "@type": "News Item",
                "title": "Parent Item",
                "image": {
                    "filename": "Horário de aulas da semana-.jpg",
                    "data": b"image-data",
                },
                "image_caption": "An example image.",
            },
            {
                "@id": "/parent/horario-de-aulas-da-semana.jpg",
                "@type": "Image",
                "id": "horario-de-aulas-da-semana.jpg",
                "title": "horario-de-aulas-da-semana.jpg",
                "image": {
                    "filename": "Horário de aulas da semana-.jpg",
                    "data": b"image-data",
                },
                "image_caption": "An example image.",
            },
        ),
    ],
)
def test_create_image_from_item(parent: t.PloneItem, expected: t.PloneItem):
    func = item.create_image_from_item
    image = func(parent)
    assert image["@id"] == expected["@id"]
    assert image.get("title") == expected["id"]
    assert image.get("image", {}).get("filename") == expected["image"]["filename"]
    assert image.get("image_caption") == expected["image_caption"]
