import json
from app.nim_client import NimClient, NimConfig


def test_post_infer_requests(mocker):
    config = NimConfig(nim_host="http://nim-host", chat_model="model", timeouts_seconds=5)
    client = NimClient(config)
    mocked = mocker.patch.object(client.session, "post")
    mocked.return_value.json.return_value = {"ok": True}
    mocked.return_value.raise_for_status.return_value = None
    resp = client.post_infer({"input": []})
    assert resp == {"ok": True}
    mocked.assert_called_once()


def test_post_chat_completions_requests(mocker):
    config = NimConfig(nim_host="http://nim-host", chat_model="model", timeouts_seconds=5)
    client = NimClient(config)
    mocked = mocker.patch.object(client.session, "post")
    mocked.return_value.json.return_value = {"choices": [{"message": {"content": "hi"}}]}
    mocked.return_value.raise_for_status.return_value = None
    resp = client.post_chat_completions([{"role": "user", "content": "hello"}])
    assert "choices" in resp
    mocked.assert_called_once()


