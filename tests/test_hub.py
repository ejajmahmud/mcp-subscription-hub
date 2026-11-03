"""Unit tests for SubscriptionHub."""
import unittest
from mcp_subscription_hub.hub import SubscriptionHub

class TestSubscriptionHub(unittest.TestCase):
    def setUp(self):
        self.hub = SubscriptionHub()

    def test_subscribe_and_publish(self):
        sub_id = self.hub.subscribe("app://events", "agent_1")
        self.assertTrue(sub_id.startswith("sub_"))
        count = self.hub.publish("app://events", {"msg": "hello"})
        self.assertEqual(count, 1)
        ntfs = self.hub.fetch_notifications("agent_1")
        self.assertEqual(len(ntfs), 1)
        self.assertEqual(ntfs[0]["data"]["msg"], "hello")

    def test_filter_function(self):
        self.hub.subscribe("app://events", "agent_filtered", filter_fn=lambda d: d.get("level") == "error")
        self.hub.publish("app://events", {"level": "info", "msg": "all good"})
        self.assertEqual(len(self.hub.fetch_notifications("agent_filtered")), 0)
        self.hub.publish("app://events", {"level": "error", "msg": "crash"})
        self.assertEqual(len(self.hub.fetch_notifications("agent_filtered")), 1)

    def test_ack_removes_notification(self):
        self.hub.subscribe("app://events", "agent_ack")
        self.hub.publish("app://events", {"val": 1})
        ntfs = self.hub.fetch_notifications("agent_ack")
        self.assertTrue(self.hub.ack("agent_ack", ntfs[0]["id"]))
        self.assertEqual(len(self.hub.fetch_notifications("agent_ack")), 0)

    def test_unsubscribe(self):
        sub_id = self.hub.subscribe("app://events", "agent_unsub")
        self.assertTrue(self.hub.unsubscribe(sub_id))
        self.assertFalse(self.hub.unsubscribe("invalid_id"))
        self.hub.publish("app://events", {"val": 1})
        self.assertEqual(len(self.hub.fetch_notifications("agent_unsub")), 0)

if __name__ == "__main__":
    unittest.main()
