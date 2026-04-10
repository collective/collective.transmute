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


class TestGenerateUid:
    def test_length(self):
        uid = item.generate_uid()
        assert len(uid) == 32

    def test_no_dashes(self):
        uid = item.generate_uid()
        assert "-" not in uid

    def test_unique(self):
        uids = {item.generate_uid() for _ in range(100)}
        assert len(uids) == 100


class TestAddRelation:
    def test_adds_single_relation(self, pipeline_state):
        metadata = pipeline_state.metadata
        metadata.relations = []
        src = {"UID": "src-uid"}
        dst = {"UID": "dst-uid"}
        item.add_relation(src, dst, "preview_image_link", metadata)
        assert len(metadata.relations) == 1
        assert metadata.relations[0] == {
            "from_attribute": "preview_image_link",
            "from_uuid": "src-uid",
            "to_uuid": "dst-uid",
        }

    def test_appends_to_existing(self, pipeline_state):
        metadata = pipeline_state.metadata
        metadata.relations = [{"existing": "relation"}]
        src = {"UID": "src-uid"}
        dst = {"UID": "dst-uid"}
        item.add_relation(src, dst, "related", metadata)
        assert len(metadata.relations) == 2


class TestAddAnnotation:
    def test_creates_annotation_for_new_uid(self, pipeline_state):
        pipeline_state.annotations = {}
        item.add_annotation("uid-1", "key1", "value1", pipeline_state)
        assert pipeline_state.annotations == {"uid-1": {"key1": "value1"}}

    def test_adds_to_existing_uid(self, pipeline_state):
        pipeline_state.annotations = {"uid-1": {"existing": "value"}}
        item.add_annotation("uid-1", "key1", "value1", pipeline_state)
        assert pipeline_state.annotations["uid-1"] == {
            "existing": "value",
            "key1": "value1",
        }

    def test_overwrites_existing_key(self, pipeline_state):
        pipeline_state.annotations = {"uid-1": {"key1": "old"}}
        item.add_annotation("uid-1", "key1", "new", pipeline_state)
        assert pipeline_state.annotations["uid-1"]["key1"] == "new"


class TestGetAnnotation:
    def test_returns_default_when_missing_uid(self, pipeline_state):
        pipeline_state.annotations = {}
        value = item.get_annotation("uid-1", "key1", "default", pipeline_state)
        assert value == "default"

    def test_returns_default_when_missing_key(self, pipeline_state):
        pipeline_state.annotations = {"uid-1": {"other": "x"}}
        value = item.get_annotation("uid-1", "key1", "default", pipeline_state)
        assert value == "default"

    def test_returns_stored_value(self, pipeline_state):
        pipeline_state.annotations = {"uid-1": {"key1": "stored"}}
        value = item.get_annotation("uid-1", "key1", "default", pipeline_state)
        assert value == "stored"

    def test_does_not_mutate(self, pipeline_state):
        pipeline_state.annotations = {"uid-1": {"key1": "stored"}}
        item.get_annotation("uid-1", "key1", "default", pipeline_state)
        assert pipeline_state.annotations == {"uid-1": {"key1": "stored"}}


class TestPopAnnotation:
    def test_returns_default_when_missing_uid(self, pipeline_state):
        pipeline_state.annotations = {}
        value = item.pop_annotation("uid-1", "key1", "default", pipeline_state)
        assert value == "default"

    def test_returns_default_when_missing_key(self, pipeline_state):
        pipeline_state.annotations = {"uid-1": {"other": "x"}}
        value = item.pop_annotation("uid-1", "key1", "default", pipeline_state)
        assert value == "default"

    def test_returns_and_removes_stored_value(self, pipeline_state):
        pipeline_state.annotations = {"uid-1": {"key1": "stored"}}
        value = item.pop_annotation("uid-1", "key1", "default", pipeline_state)
        assert value == "stored"
        assert "key1" not in pipeline_state.annotations["uid-1"]
