import unittest

from dummy_dialogue_server.app import create_app


class DummyDialogueServerTest(unittest.TestCase):
    def setUp(self):
        self.app, self.socketio = create_app()
        self.client = self.socketio.test_client(self.app)

    def tearDown(self):
        self.client.disconnect()

    def test_text_message_returns_frontend_compatible_response(self):
        self.client.emit("user_message", "What should I do about a fever?")

        received = self.client.get_received()
        system_messages = [
            event["args"][0]
            for event in received
            if event["name"] == "system_message"
        ]

        self.assertEqual(len(system_messages), 1)
        self.assertEqual(system_messages[0]["type"], "text")
        self.assertIn("fever", system_messages[0]["system_text"].lower())
        self.assertGreaterEqual(len(system_messages[0]["snippet"]), 1)
        self.assertIn("data", system_messages[0]["snippet"][0])

    def test_voice_message_returns_frontend_compatible_response(self):
        self.client.emit("user_voice", {"audio": "data:audio/webm;base64,AAAA"})

        received = self.client.get_received()
        system_messages = [
            event["args"][0]
            for event in received
            if event["name"] == "system_message"
        ]

        self.assertEqual(len(system_messages), 1)
        self.assertEqual(system_messages[0]["type"], "text")
        self.assertIn("voice", system_messages[0]["system_text"].lower())


if __name__ == "__main__":
    unittest.main()
