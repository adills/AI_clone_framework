import os
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from agent import agent
import sys
import json
import re
import logging

# Initializes your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.error
def global_error_handler(error, body, logger):
    # Surface any Bolt errors and the triggering payload to stdout/stderr
    logger.exception(f"[BOLT ERROR] {error}")
    logger.info(f"[BOLT BODY] {body}")

# A dictionary to store chat histories per user
chat_histories = {}

# --- Simple live E2E check inside Slack (no agent required) ---
# If you DM or @mention the bot with "ping", it should reply "pong".
PING_PATTERN = re.compile(r"^ping$", re.IGNORECASE)
FALLBACK_PATTERN = re.compile(r"^(?!ping$).+", re.IGNORECASE)  # anything that's not exactly "ping"

@app.message(PING_PATTERN)
def ping_handler(message, say):
    """Fast live-check: verifies events are reaching the bot and it can reply."""
    say("pong")

@app.message(FALLBACK_PATTERN)
def message_handler(message, say):
    """Handles messages sent to the bot (non-ping), forwarding to the agent."""
    user_id = message.get("user", "")
    user_message = message.get("text", "")

    # Self-test mode bypasses the real agent to avoid external dependencies.
    if os.getenv("AI_CLONE_TEST_MODE") == "1":
        response = f"[SELFTEST OK] Echo: {user_message}"
    else:
        # Pass the user_id to the agent function
        response = agent(user_message, user_id)

    say(response)

@app.event("app_mention")
def handle_app_mention(body, say, logger):
    event = body.get("event", {})
    logger.info(f"[EVENT] app_mention in {event.get('channel')} from {event.get('user')}: {event.get('text')}")
    say("pong (mention)")

@app.event("message")
def log_message_events(body, logger):
    event = body.get("event", {})
    # Avoid echo loops by not logging bot messages
    if event.get("subtype") == "bot_message":
        return
    logger.debug(f"[EVENT] message in {event.get('channel')} from {event.get('user')}: {event.get('text')}")

def _selftest() -> int:
    """
    Local functional test that simulates a DM reaching the message handler and verifies
    that a response would be sent. This does not call Slack APIs and does not require tokens.
    It confirms end-to-end handling within this process: handler -> (agent or stub) -> say().
    Returns 0 on success, 1 on failure.
    """
    # Ensure test mode so we don't require the real agent/model
    os.environ["AI_CLONE_TEST_MODE"] = os.getenv("AI_CLONE_TEST_MODE", "1")

    fake_message = {"user": "U_TESTSELF", "text": "Hello from selftest"}
    captured = []

    def fake_say(text: str):
        captured.append(str(text))

    try:
        # Call the same handler Slack would invoke
        message_handler(fake_message, fake_say)
    except Exception as e:
        print(json.dumps({"result": "fail", "reason": f"exception: {e}"}))
        return 1

    ok = any(msg.startswith("[SELFTEST OK]") for msg in captured)
    print(json.dumps({"result": "pass" if ok else "fail", "captured": captured}))
    return 0 if ok else 1

# Start your app
if __name__ == "__main__":
    # Usage:
    #   python slack_bot.py --selftest   -> runs local functional test (no Slack network required)
    #   python slack_bot.py              -> starts Socket Mode bot (requires env tokens)
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    # Optional: honor SLACK_LOG_LEVEL (e.g., DEBUG/INFO/WARNING)
    lvl = os.getenv("SLACK_LOG_LEVEL", "INFO").upper()
    logging.basicConfig(level=getattr(logging, lvl, logging.INFO), format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
