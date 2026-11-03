"""Core Subscription Hub implementation for MCP resources."""
import uuid
import time
from typing import Dict, List, Any, Optional, Callable


class SubscriptionHub:
    def __init__(self):
        self._subscriptions: Dict[str, Dict[str, Any]] = {}
        self._queues: Dict[str, List[Dict[str, Any]]] = {}

    def subscribe(self, uri: str, subscriber_id: str, filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None) -> str:
        sub_id = f"sub_{uuid.uuid4().hex[:8]}"
        self._subscriptions[sub_id] = {
            "uri": uri,
            "subscriber_id": subscriber_id,
            "filter_fn": filter_fn,
            "created_at": time.time()
        }
        if subscriber_id not in self._queues:
            self._queues[subscriber_id] = []
        return sub_id

    def unsubscribe(self, sub_id: str) -> bool:
        if sub_id in self._subscriptions:
            del self._subscriptions[sub_id]
            return True
        return False

    def publish(self, uri: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> int:
        delivered_count = 0
        now = time.time()
        for sub_id, sub in self._subscriptions.items():
            if sub["uri"] == uri or sub["uri"] == "*":
                filter_fn = sub.get("filter_fn")
                if filter_fn and not filter_fn(data):
                    continue
                notification = {
                    "id": f"ntf_{uuid.uuid4().hex[:8]}",
                    "sub_id": sub_id,
                    "uri": uri,
                    "data": data,
                    "metadata": metadata or {},
                    "timestamp": now,
                    "acked": False
                }
                self._queues[sub["subscriber_id"]].append(notification)
                delivered_count += 1
        return delivered_count

    def fetch_notifications(self, subscriber_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        queue = self._queues.get(subscriber_id, [])
        unacked = [n for n in queue if not n["acked"]]
        return unacked[:limit]

    def ack(self, subscriber_id: str, notification_id: str) -> bool:
        queue = self._queues.get(subscriber_id, [])
        for n in queue:
            if n["id"] == notification_id:
                n["acked"] = True
                queue.remove(n)
                return True
        return False

    def stats(self) -> Dict[str, Any]:
        total_queued = sum(len(q) for q in self._queues.values())
        return {
            "active_subscriptions": len(self._subscriptions),
            "subscribers": len(self._queues),
            "total_pending_notifications": total_queued
        }
