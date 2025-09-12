"""
Item utilities for collective.transmute.

This module provides helper functions for generating UIDs, handling parent paths,
creating image items, and managing relations in the transformation pipeline.
Functions are documented for Sphinx autodoc and support common item operations.
"""

from collective.transmute import _types as t
from uuid import uuid4


def generate_uid() -> str:
    """
    Generate a new UID for an item.

    Returns
    -------
    str
        A unique identifier string without dashes.

    Example
    -------
    >>> uid = generate_uid()
    >>> len(uid) == 32
    True
    """
    uid = str(uuid4())
    return uid.replace("-", "")


def all_parents_for(id_: str) -> set[str]:
    """
    Given an @id, return all possible parent paths.

    Parameters
    ----------
    id_ : str
        The item id (path) to process.

    Returns
    -------
    set[str]
        A set of all parent paths for the given id.

    Example
    -------
    >>> all_parents_for('a/b/c')
    {'a', 'a/b'}
    """
    parents = []
    parts = id_.split("/")
    for idx in range(len(parts)):
        parent_path = "/".join(parts[:idx])
        if not parent_path.strip():
            continue
        parents.append(parent_path)
    return set(parents)


def create_image_from_item(parent: t.PloneItem) -> t.PloneItem:
    """
    Create a new image object to be placed inside the parent item.

    Parameters
    ----------
    parent : PloneItem
        The parent item containing image data.

    Returns
    -------
    PloneItem
        A new image item dictionary.

    Example
    -------
    >>> parent = {'@id': 'folder', 'image': {'filename': 'img.png'}}
    >>> img_item = create_image_from_item(parent)
    >>> img_item['@type']
    'Image'
    """
    image: dict = parent.pop("image")
    image_caption: str = parent.pop("image_caption", "")
    filename: str = image["filename"]
    image_id = filename
    path = f"{parent['@id']}/{image_id}"
    item: t.PloneItem = {
        "@id": path,
        "@type": "Image",
        "image": image,
        "id": image_id,
        "title": image_id,
        "image_caption": image_caption,
        "exclude_from_nav": True,
        "UID": generate_uid(),
        "_is_new_item": True,
    }
    return item


def add_relation(
    src_item: t.PloneItem,
    dst_item: t.PloneItem,
    attribute: str,
    metadata: t.MetadataInfo,
):
    """
    Add a new relation to the relations list in metadata.

    Parameters
    ----------
    src_item : PloneItem
        The source item for the relation.
    dst_item : PloneItem
        The destination item for the relation.
    attribute : str
        The attribute name for the relation.
    metadata : MetadataInfo
        The metadata object to update.
    """
    relation = {
        "from_attribute": attribute,
        "from_uuid": src_item["UID"],
        "to_uuid": dst_item["UID"],
    }
    metadata.relations.append(relation)
