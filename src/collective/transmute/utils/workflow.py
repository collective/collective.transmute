from collective.transmute._types import PloneItem
from collective.transmute.settings import get_settings
from functools import cache


@cache
def rewrite_settings() -> dict:
    settings = get_settings()
    wf_settings = settings.review_state["rewrite"]
    if "workflows" not in wf_settings:
        wf_settings["workflows"] = {}
    if "states" not in wf_settings:
        wf_settings["states"] = {}
    return dict(wf_settings)


def rewrite_workflow_history(item: PloneItem) -> PloneItem:
    """Rewrite review_state and workflow_history for an item.

    Configuration should be added to transmute.toml

    ```toml
    [review_state.rewrite]
    states = {"visible": "published"}
    workflows = {"plone_workflow": "simple_publication_workflow"}
    ```
    """
    settings = rewrite_settings()
    review_state = item.get("review_state")
    if new_state := settings["states"].get(review_state):
        item["review_state"] = new_state
    cur_workflow_history = item.get("workflow_history")
    if cur_workflow_history:
        workflow_history = {}
        for workflow_id, actions in cur_workflow_history.items():
            new_workflow_id = settings["workflows"].get(workflow_id)
            if not new_workflow_id:
                workflow_history[workflow_id] = actions
                continue
            workflow_history[new_workflow_id] = []
            for action in actions:
                action_state = action.get("review_state")
                action["review_state"] = settings["states"].get(
                    action_state, action_state
                )
            workflow_history[new_workflow_id].append(action)
        item["workflow_history"] = workflow_history
    return item
