import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path


class DummyFilter:
    @staticmethod
    def llm_tool(**_kwargs): return lambda function: function
    @staticmethod
    def command(*_args, **_kwargs): return lambda function: function


class DummyStar:
    def __init__(self, context=None): self.context = context


astrbot = types.ModuleType("astrbot")
api = types.ModuleType("astrbot.api")
event = types.ModuleType("astrbot.api.event")
star = types.ModuleType("astrbot.api.star")
api.logger = types.SimpleNamespace(info=lambda *_: None, warning=lambda *_: None)
event.AstrMessageEvent = object
event.filter = DummyFilter
star.Context = object
star.Star = DummyStar
sys.modules.update({"astrbot": astrbot, "astrbot.api": api, "astrbot.api.event": event, "astrbot.api.star": star})

spec = importlib.util.spec_from_file_location("private_parlor", Path(__file__).parents[1] / "main.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PluginTests(unittest.TestCase):
    def make_plugin(self):
        plugin = module.AtherloomParlorPlugin(None)
        plugin.access_token = "test-token"
        calls = []

        async def request(path, payload, method="POST"):
            calls.append((path, payload, method))
            if path.endswith("redeem"):
                return {"parlor_id": "room", "expires_at": 1776086700, "visibility": "summary"}
            if path.endswith("/room"):
                return {"status": "active", "self_client_id": "self", "expires_at": 1776086700, "visibility": "summary"}
            if "messages?after=" in path:
                return {"items": [{"id": "m1", "sender_id": "other", "body": "hello", "turn_no": 1}]}
            if path.endswith("messages"):
                return {"id": "m2", "remaining_seconds": 230}
            if path.endswith("votes"):
                return {"status": "open", "kind": payload["kind"], "choice": payload["choice"]}
            return {"ended": True}

        plugin._request = request
        return plugin, calls

    def test_connect_receive_send_and_close_are_serial(self):
        plugin, calls = self.make_plugin()
        connected = asyncio.run(plugin._dispatch("connect", code="AT-test"))
        self.assertEqual(connected["duration_seconds"], 300)
        received = asyncio.run(plugin._dispatch("receive"))
        self.assertEqual(received["new_messages"][0]["body"], "hello")
        vote = asyncio.run(plugin._dispatch("vote", kind="topic", value="如何整理共同创作", choice="approve"))
        self.assertEqual(vote["kind"], "topic")
        sent = asyncio.run(plugin._dispatch("send", content="hello"))
        self.assertEqual(sent["id"], "m2")
        asyncio.run(plugin._dispatch("close", summary="ended"))
        self.assertEqual(plugin.room_token, "")
        self.assertEqual([path for path, _, _ in calls], [
            "/v1/invites/redeem", "/v1/parlors/room", "/v1/parlors/room/messages?after=0",
            "/v1/parlors/room/votes", "/v1/parlors/room/messages", "/v1/parlors/room/close",
        ])

    def test_cannot_send_without_invitation(self):
        plugin, _ = self.make_plugin()
        with self.assertRaisesRegex(ValueError, "尚未"):
            asyncio.run(plugin._dispatch("send", content="hello"))

    def test_policy_names_privacy_nsfw_social_engineering_and_five_minutes(self):
        self.assertIn("五分钟", module.POLICY)
        self.assertIn("NSFW", module.POLICY)
        self.assertIn("社会工程", module.POLICY)
        self.assertIn("用户隐私", module.POLICY)


if __name__ == "__main__":
    unittest.main()
