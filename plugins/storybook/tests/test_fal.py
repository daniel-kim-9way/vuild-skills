import base64
import io
import json
import urllib.error

from storybook import fal, painter, story
from storybook.painter import PaintError, RetryablePaintError
from tests.helpers import HomeTestCase, make_story
from tests.test_painter import png


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def answer(payload: dict):
    calls = []

    def opener(req, timeout):
        calls.append(req)
        return Response(json.dumps(payload).encode())

    return opener, calls


def http_error(code: int, body: bytes = b"{}"):
    def opener(req, timeout):
        raise urllib.error.HTTPError("https://fal.run", code, "error", {}, io.BytesIO(body))

    return opener


class FalTest(HomeTestCase):
    def setUp(self):
        super().setUp()
        folder = make_story(images=False)
        data = story.load(folder)
        self.request = painter.request_for(data, data["pages"][1], folder)
        self.picture = "data:image/jpeg;base64," + base64.b64encode(png()).decode()

    def test_request_shape(self):
        opener, calls = answer({"images": [{"url": self.picture}]})
        raw = fal.FalEngine(key="test-key", opener=opener).paint(self.request, 1)
        self.assertEqual(raw, png())
        req = calls[0]
        self.assertEqual(req.full_url, "https://fal.run/fal-ai/flux-2-pro/edit")
        self.assertEqual(req.get_header("Authorization"), "Key test-key")
        body = json.loads(req.data)
        self.assertTrue(body["sync_mode"])
        self.assertEqual(body["image_size"], {"width": 1024, "height": 768})
        self.assertEqual(body["seed"], self.request.seed)
        self.assertEqual(len(body["image_urls"]), 2)
        self.assertTrue(body["image_urls"][0].startswith("data:image/jpeg;base64,"))

    def test_second_try_changes_seed(self):
        body = fal.FalEngine(key="k", opener=None).body(self.request, 2)
        self.assertIsInstance(body["seed"], int)

    def test_safety_block_is_retryable(self):
        opener, _ = answer({"images": [{"url": self.picture}], "has_nsfw_concepts": [True]})
        with self.assertRaises(RetryablePaintError):
            fal.FalEngine(key="k", opener=opener).paint(self.request, 1)

    def test_wrong_key_and_empty_balance_stop(self):
        # fal은 잔액이 떨어지면 403에 «User is locked. Reason: Exhausted balance»를 보낸다
        for code, body, words in ((401, b"{}", "키가 맞지 않아요"), (403, b"{}", "키가 맞지 않아요"),
                                  (403, b"{\"detail\": \"User is locked. Reason: Exhausted balance\"}", "잔액"),
                                  (402, b"{}", "잔액")):
            with self.assertRaises(PaintError) as caught:
                fal.FalEngine(key="k", opener=http_error(code, body)).paint(self.request, 1)
            self.assertNotIsInstance(caught.exception, RetryablePaintError)
            self.assertIn(words, str(caught.exception))

    def test_busy_server_is_retryable(self):
        for code in (429, 503):
            with self.assertRaises(RetryablePaintError):
                fal.FalEngine(key="k", opener=http_error(code)).paint(self.request, 1)

    def test_missing_key_stops(self):
        with self.assertRaises(PaintError):
            fal.FalEngine(key=None, opener=None)

    def test_estimate(self):
        self.assertEqual(fal.estimate(9), "9장, 720~1,170원쯤")
