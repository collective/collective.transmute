from collective.transmute._types.plone import WorkflowHistoryEntry


def from_one_state_workflow(
    settings: dict,
    actions: list[WorkflowHistoryEntry],
) -> list[WorkflowHistoryEntry]:
    """
    Convert a list of workflow actions from a one-state workflow to a valid
    simple publication workflow format.

    Parameters
    ----------
    actions : list of actions
        The original list of workflow actions.

    ```
        [
            {
                "action": null,
                "actor": "1887028",
                "comments": "",
                "review_state": "published",
                "time": "2016-10-25T12:07:33+00:00"
            }
        ]
    ```

    Returns
    -------
    list of actions
        The converted list of workflow actions.
    """
    new_actions = []
    action = actions[0] if actions else {}
    if not action:
        action = {
            "action": None,
            "actor": "system",
            "comments": "No previous workflow history",
            "review_state": "private",
            "time": "1970-01-01T00:00:00+00:00",
        }
    else:
        action["review_state"] = "private"
    new_actions.append(action)
    publish = action.copy()
    publish["action"] = "publish"
    publish["comments"] = "Published during migration"
    publish["review_state"] = "published"
    new_actions.append(publish)
    return new_actions
