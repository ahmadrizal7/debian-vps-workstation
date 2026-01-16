import unittest

from configurator.ux.history import ConfigHistory


class TestHistory(unittest.TestCase):
    def test_save_state(self):
        history = ConfigHistory(max_size=5)
        state1 = {"a": 1}
        history.save_state(state1)
        self.assertTrue(history.can_undo())

    def test_undo_redo(self):
        history = ConfigHistory()
        history.save_state({"step": 1})
        history.save_state({"step": 2})

        current = {"step": 3}
        previous = history.undo(current)
        self.assertEqual(previous["step"], 2)

        previous = history.undo(previous)
        self.assertEqual(previous["step"], 1)

        future = history.redo(previous)
        self.assertEqual(future["step"], 2)

    def test_max_size(self):
        history = ConfigHistory(max_size=2)
        history.save_state({"1": 1})
        history.save_state({"2": 2})
        history.save_state({"3": 3})
        # Should have popped 1, so internal stack is [2, 3] roughly
        # Actually save_state appends to undo_stack.
        # stack: [1] -> [1, 2] -> [2, 3]

        # Current state is assumed separate. Undo pops from stack.
        # current=4. undo() -> pops 3.
        # If we undo again -> pops 2.
        # If we undo again -> empty/None

        mock_current = {"current": 4}
        s3 = history.undo(mock_current)
        self.assertEqual(s3["3"], 3)
        s2 = history.undo(s3)
        self.assertEqual(s2["2"], 2)
        s1 = history.undo(s2)
        self.assertIsNone(s1)
