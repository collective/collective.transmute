"""
Workflow utilities for ``collective.transmute``.

This module provides helper functions for rewriting workflow history and review states
in Plone items during the transformation pipeline. Functions support
configuration-driven workflow normalization and migration.
"""

from collective.transmute._types import PloneItem
from collective.transmute._types import WorkflowHistoryEntry
from collective.transmute.settings import get_settings
from collective.transmute.utils.workflow import simple_publication_workflow
from functools import cache


_HISTORY_REWRITERS = {
    "simple_publication_workflow": {
        "one_state_workflow": simple_publication_workflow.from_one_state_workflow,
    }
}


def _default_rewrite(
    settings: dict,
    actions: list[WorkflowHistoryEntry],
) -> list[WorkflowHistoryEntry]:
    """
    Convert a list of workflow actions.

    Parameters
    ----------
    actions : list of actions
        The original list of workflow actions.

    Returns
    -------
    list of actions
        The converted list of workflow actions.
    """
    new_actions = []
    for action in actions:
        action_state = action.get("review_state")
        action["review_state"] = settings["states"].get(action_state, action_state)
        new_actions.append(action)
    return new_actions


@cache
def rewrite_settings() -> dict:
    """
    Return workflow rewrite settings from the transmute configuration.

    Returns
    -------
    dict
        Dictionary containing workflow and state rewrite mappings.

    Example
    -------
    .. code-block:: pycon

        >>> settings = rewrite_settings()
        >>> settings['states']
        {'visible': 'published'}
    """
    settings = get_settings()
    wf_settings = settings.review_state["rewrite"]
    if "workflows" not in wf_settings:
        wf_settings["workflows"] = {}
    if "states" not in wf_settings:
        wf_settings["states"] = {}
    return dict(wf_settings)


def rewrite_workflow_history(item: PloneItem) -> PloneItem:
    """
    Rewrite ``review_state`` and ``workflow_history`` for a Plone item.

    Configuration should be added to ``transmute.toml``, for example:

    .. code-block:: toml

        [review_state.rewrite]
        states = {"visible" = "published"}
        workflows = {"plone_workflow" = "simple_publication_workflow"}

    Parameters
    ----------
    item : PloneItem
        The item whose workflow history and review state will be rewritten.

    Returns
    -------
    PloneItem
        The updated item with rewritten workflow history and review state.

    Example
    -------
    .. code-block:: pycon

        >>> item = {'review_state': 'visible', 'workflow_history': {...}}
        >>> rewrite_workflow_history(item)
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
            rewriter = _HISTORY_REWRITERS.get(new_workflow_id, {}).get(
                workflow_id, _default_rewrite
            )
            workflow_history[new_workflow_id] = rewriter(settings, actions)
        item["workflow_history"] = workflow_history
    return item
