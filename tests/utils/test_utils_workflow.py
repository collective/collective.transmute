import pytest


@pytest.fixture
def rewrite_settings(monkeypatch):
    settings = {
        "states": {
            "private": "private",
            "visible": "published",
        },
        "workflows": {
            "plone_workflow": "simple_publication_workflow",
            "one_state_workflow": "simple_publication_workflow",
        },
    }
    monkeypatch.setattr(
        "collective.transmute.utils.workflow.rewrite_settings", lambda: settings
    )


@pytest.fixture
def item_plone_workflow(load_json_resource) -> dict:
    return load_json_resource("workflows/plone_workflow.json")


def test_rewrite_workflow_history_plone_workflow(rewrite_settings, item_plone_workflow):
    from collective.transmute.utils import workflow

    func = workflow.rewrite_workflow_history
    result = func(item_plone_workflow)
    assert result.get("review_state") == "published"
    history = result.get("workflow_history", {})
    assert "plone_workflow" not in history
    assert "simple_publication_workflow" in history


@pytest.fixture
def item_one_state_workflow(load_json_resource) -> dict:
    return load_json_resource("workflows/one_state_workflow.json")


def test_rewrite_workflow_history_one_state_workflow(
    rewrite_settings, item_one_state_workflow
):
    from collective.transmute.utils import workflow

    func = workflow.rewrite_workflow_history
    result = func(item_one_state_workflow)
    assert result.get("review_state") == "published"
    history = result.get("workflow_history", {})
    assert "one_state_workflow" not in history
    assert "simple_publication_workflow" in history
    actions = history.get("simple_publication_workflow", [])
    assert len(actions) == 2
    assert actions[0]["review_state"] == "private"
    assert actions[1]["review_state"] == "published"
    assert actions[1]["action"] == "publish"
    assert actions[1]["comments"] == "Published during migration"
