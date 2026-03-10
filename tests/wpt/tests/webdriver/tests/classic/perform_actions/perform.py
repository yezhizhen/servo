import pytest

from tests.support.asserts import assert_success
from . import perform_actions


@pytest.mark.parametrize("action_type", ["none", "key", "pointer", "wheel"])
def test_input_source_action_sequence_actions_pause_duration_valid(
    session, action_type
):
    for valid_duration in [0, 1]:
        actions = [
            {
                "type": action_type,
                "id": "foo",
                "actions": [{"type": "pause", "duration": valid_duration}],
            }
        ]
        response = perform_actions(session, actions)
        assert_success(response)


@pytest.mark.parametrize("action_type", ["none", "key", "pointer", "wheel"])
def test_input_source_action_sequence_actions_pause_duration_missing(
    session, action_type
):
    actions = [
        {
            "type": action_type,
            "id": "foo",
            "actions": [
                {
                    "type": "pause",
                }
            ],
        }
    ]
    response = perform_actions(session, actions)
    assert_success(response)


@pytest.mark.parametrize("action_type", ["none", "key", "wheel"])
def test_input_source_action_sequence_pointer_parameters_not_processed(
    session, action_type
):
    actions = [
        {
            "type": action_type,
            "id": "foo",
            "actions": [],
            "parameters": True,
        }
    ]
    response = perform_actions(session, actions)
    assert_success(response)


def test_interspersed_wheel_pointermove(session, wheel_chain, mouse_chain, inline):
    session.url = inline("""
        <div id='target' style='width: 200px; height: 200px; background: red;'></div>
        <script>
            window.events = [];
            target.onwheel = () => window.events.push('wheel');
            target.onmousemove = () => window.events.push('move');
        </script>
    """)

    target = session.find.css("#target", all=False)

    wheel_chain.scroll(0, 0, 0, 100, duration=150, origin=target)
    mouse_chain.pointer_move(80, 80, duration=150, origin=target)

    session.actions.perform([wheel_chain.dict, mouse_chain.dict])

    events = session.execute_script("return window.events")

    assert "wheel" in events
    assert "move" in events

    # the first 'move' should appear before the last 'scroll'
    first_move = events.index("move")
    last_scroll = len(events) - 1 - events[::-1].index("wheel")

    assert first_move < last_scroll, f"Events were not interspersed: {events}"
