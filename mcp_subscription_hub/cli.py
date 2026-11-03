"""Command-line interface for MCP Subscription Hub."""
import argparse
from .hub import SubscriptionHub

def main():
    parser = argparse.ArgumentParser(description="MCP Subscription Hub CLI")
    parser.add_argument("--demo", action="store_true", help="Run self-test pub/sub demonstration")
    args = parser.parse_args()

    hub = SubscriptionHub()
    sub_id = hub.subscribe("resources://files/updates", "agent_worker_1")
    hub.publish("resources://files/updates", {"file": "main.py", "action": "modified"})
    notifications = hub.fetch_notifications("agent_worker_1")
    print(f"Hub operational. Captured {len(notifications)} notification(s).")
    if notifications:
        hub.ack("agent_worker_1", notifications[0]["id"])
        print(f"Notification acked. Pending count: {len(hub.fetch_notifications('agent_worker_1'))}")
    print("Stats:", hub.stats())

if __name__ == "__main__":
    main()
