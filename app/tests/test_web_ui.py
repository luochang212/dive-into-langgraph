import asyncio
import gc
import unittest

from utils import web_ui


def _streaming_dummy(message, history):
    yield "", history


def _blocks_by_type(ui, type_name):
    return [
        block
        for block in ui.blocks.values()
        if type(block).__name__ == type_name
    ]


def _create_test_ui(test_case):
    loops = []
    original_new_event_loop = asyncio.new_event_loop

    def track_new_event_loop():
        loop = original_new_event_loop()
        loops.append(loop)
        return loop

    asyncio.new_event_loop = track_new_event_loop
    try:
        ui = web_ui.create_ui(_streaming_dummy, "Test Tab", "Test App")
    finally:
        asyncio.new_event_loop = original_new_event_loop

    def cleanup():
        ui.close()
        for loop in loops:
            if not loop.is_closed():
                loop.close()
        gc.collect()

    test_case.addCleanup(cleanup)
    return ui


class ButtonStateTests(unittest.TestCase):
    def test_show_stop_button_hides_send_and_shows_stop(self):
        self.assertTrue(hasattr(web_ui, "_show_stop_button"))

        send_update, stop_update = web_ui._show_stop_button()

        self.assertFalse(send_update["visible"])
        self.assertTrue(stop_update["visible"])

    def test_show_send_button_shows_send_and_hides_stop(self):
        self.assertTrue(hasattr(web_ui, "_show_send_button"))

        send_update, stop_update = web_ui._show_send_button()

        self.assertTrue(send_update["visible"])
        self.assertFalse(stop_update["visible"])

    def test_stop_generation_clears_active_typing_indicator(self):
        self.assertTrue(hasattr(web_ui, "_stop_generation"))

        send_update, stop_update, history = web_ui._stop_generation([
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": '<span class="typing-indicator"></span>'},
        ])

        self.assertTrue(send_update["visible"])
        self.assertFalse(stop_update["visible"])
        self.assertEqual(history[-1], {"role": "assistant", "content": ""})

    def test_stop_generation_does_not_clear_text_that_mentions_typing_indicator(self):
        _, _, history = web_ui._stop_generation([
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "The CSS class is typing-indicator."},
        ])

        self.assertEqual(
            history[-1],
            {"role": "assistant", "content": "The CSS class is typing-indicator."},
        )


class CreateUiTests(unittest.TestCase):
    def test_create_ui_adds_hidden_stop_button(self):
        ui = _create_test_ui(self)

        buttons = _blocks_by_type(ui, "Button")
        button_values = [button.value for button in buttons]

        self.assertIn("发送", button_values)
        self.assertIn("中止", button_values)

        stop_button = next(button for button in buttons if button.value == "中止")
        self.assertFalse(stop_button.visible)
        self.assertEqual(stop_button.variant, "stop")

    def test_stop_button_cancels_enter_and_click_generation_events(self):
        ui = _create_test_ui(self)

        chatbot = _blocks_by_type(ui, "Chatbot")[0]
        textbox = _blocks_by_type(ui, "Textbox")[0]
        buttons = _blocks_by_type(ui, "Button")
        button_values = [button.value for button in buttons]
        self.assertIn("发送", button_values)
        self.assertIn("中止", button_values)

        send_button = next(button for button in buttons if button.value == "发送")
        stop_button = next(button for button in buttons if button.value == "中止")

        generation_fn_indices = {
            index
            for index, fn in ui.fns.items()
            if getattr(fn, "targets", None) == [(None, "then")]
            and [component._id for component in fn.inputs] == [textbox._id, chatbot._id]
            and [component._id for component in fn.outputs] == [textbox._id, chatbot._id]
        }
        self.assertEqual(len(generation_fn_indices), 2)

        stop_state_events = [
            fn
            for fn in ui.fns.values()
            if getattr(fn, "targets", None) == [(stop_button._id, "click")]
            and [component._id for component in fn.inputs] == [chatbot._id]
            and [component._id for component in fn.outputs]
            == [send_button._id, stop_button._id, chatbot._id]
        ]
        self.assertEqual(len(stop_state_events), 1)

        stop_cancel_events = [
            fn
            for fn in ui.fns.values()
            if getattr(fn, "targets", None) == [(stop_button._id, "click")]
            and set(getattr(fn, "cancels", [])) == generation_fn_indices
        ]
        self.assertEqual(len(stop_cancel_events), 1)


if __name__ == "__main__":
    unittest.main()
