import asyncio
import importlib.util
import sys
import types
import unittest
from pathlib import Path


class DummyFilter:
    @staticmethod
    def llm_tool(**_kwargs):
        return lambda function: function

    @staticmethod
    def command(*_args, **_kwargs):
        return lambda function: function


class DummyStar:
    def __init__(self, context=None):
        self.context = context


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
        calls = []

        async def request(path, payload):
            calls.append((path, payload))
            if path.endswith("redeem"):
                return {"room_token":"x"*32,"room_id":"room","ends_at":"2026-08-14T00:05:00Z","visibility":"summary"}
            if path.endswith("status"):
                return {"status":"active","remaining_seconds":240,"ends_at":"2026-08-14T00:05:00Z","visibility":"summary","end_reason":"","messages":[{"id":"m1","speaker":"host","content":"你好"}]}
            if path.endswith("message"):
                return {"id":"m2","remaining_seconds":230}
            return {"ended":True}

        plugin._request = request
        return plugin, calls

    def test_connect_receive_send_and_close_are_serial(self):
        plugin, calls = self.make_plugin()
        connected = asyncio.run(plugin._dispatch("connect", code="AT-test"))
        self.assertEqual(connected["duration_seconds"], 300)
        received = asyncio.run(plugin._dispatch("receive"))
        self.assertEqual(received["new_host_messages"][0]["content"], "你好")
        sent = asyncio.run(plugin._dispatch("send", content="很高兴见到你"))
        self.assertEqual(sent["id"], "m2")
        asyncio.run(plugin._dispatch("close", summary="礼貌地聊了近况。"))
        self.assertEqual(plugin.room_token, "")
        self.assertEqual([path for path, _ in calls], [
            "/api/correspondence/invites/redeem", "/api/correspondence/parlors/status",
            "/api/correspondence/parlors/message", "/api/correspondence/parlors/close",
        ])

    def test_cannot_send_without_invitation(self):
        plugin, _ = self.make_plugin()
        with self.assertRaisesRegex(ValueError, "邀请码"):
            asyncio.run(plugin._dispatch("send", content="你好"))

    def test_policy_names_privacy_nsfw_social_engineering_and_five_minutes(self):
        self.assertIn("五分钟", module.POLICY)
        self.assertIn("NSFW", module.POLICY)
        self.assertIn("社会工程", module.POLICY)
        self.assertIn("用户隐私", module.POLICY)


if __name__ == "__main__":
    unittest.main()
