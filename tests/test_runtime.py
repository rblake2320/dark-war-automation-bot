import unittest

from darkwar_operator.runtime import Action, Risk, ScreenState, UnsafeAction, VerifiedRuntime


class FakeDevice:
    def __init__(self, states):
        self.states = iter(states)
        self.actions = []

    def observe(self):
        return next(self.states)

    def act(self, action):
        self.actions.append(action)


class RuntimeTests(unittest.TestCase):
    def test_executes_only_when_verified(self):
        device = FakeDevice([ScreenState("base", frozenset({"mail"})), ScreenState("base")])
        runtime = VerifiedRuntime(device)
        action = Action("collect_mail", "mail", expected="mail badge disappears")
        after = runtime.execute(action, lambda before, current: "mail" in before.indicators and "mail" not in current.indicators)
        self.assertEqual(after.location, "base")
        self.assertEqual([item.id for item in device.actions], ["collect_mail"])

    def test_blocks_purchase_before_clicking(self):
        device = FakeDevice([ScreenState("offer")])
        runtime = VerifiedRuntime(device)
        with self.assertRaises(UnsafeAction):
            runtime.execute(Action("buy", "offer", Risk.PURCHASE), lambda *_: True)
        self.assertEqual(device.actions, [])

    def test_blocks_low_confidence_before_clicking(self):
        device = FakeDevice([ScreenState("base", confidence=0.2)])
        runtime = VerifiedRuntime(device)
        with self.assertRaises(UnsafeAction):
            runtime.execute(Action("collect", "mail"), lambda *_: True)
        self.assertEqual(device.actions, [])


if __name__ == "__main__":
    unittest.main()
