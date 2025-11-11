import os
import yaml
import json
from datetime import datetime
from typing import Dict, Any
import google.generativeai as legacy_genai
from dotenv import load_dotenv
from serpapi import GoogleSearch
from trello import TrelloClient
from github import Github

load_dotenv()

# --- Load configuration ---
with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

# --- Ensure logs directory exists ---
LOG_FILE_PATH = CONFIG["logging"]["path"]
LOG_DIR = os.path.dirname(LOG_FILE_PATH)
os.makedirs(LOG_DIR, exist_ok=True)


# --- Tool Implementations ---

def web_search(query: str) -> str:
    """Performs a web search."""
    search = GoogleSearch({
        "q": query,
        "api_key": os.environ["SERPAPI_API_KEY"]
    })
    result = search.get_dict()
    return str(result.get("organic_results", "No results found."))

def trello_create_card(card_title: str, description: str = None) -> str:
    """Creates a Trello card."""
    try:
        client = TrelloClient(
            api_key=os.environ["TRELLO_API_KEY"],
            api_secret=os.environ["TRELLO_API_TOKEN"],
        )
        list_id = CONFIG["tools"]["trello"]["list_id"]
        all_boards = client.list_boards()
        target_list = None
        for board in all_boards:
            for trello_list in board.list_lists():
                if trello_list.id == list_id:
                    target_list = trello_list
                    break
            if target_list:
                break

        if target_list:
            new_card = target_list.add_card(name=card_title, desc=description)
            return f"Successfully created Trello card: '{new_card.name}' in list '{target_list.name}'."
        else:
            return f"Error: Could not find a Trello list with ID '{list_id}'."
    except Exception as e:
        return f"Error creating Trello card: {e}"

def github_search(query: str) -> str:
    """Searches GitHub for repositories."""
    try:
        g = Github(os.environ["GITHUB_TOKEN"])
        repositories = g.search_repositories(query)
        results = []
        for i, repo in enumerate(repositories):
            if i >= 5: # Limit to the top 5 results
                break
            results.append(
                f"{i+1}. {repo.full_name}: {repo.description}\n"
                f"   URL: {repo.html_url}\n"
                f"   Stars: {repo.stargazers_count}"
            )
        return "\n".join(results) if results else "No repositories found."
    except Exception as e:
        return f"Error searching GitHub: {e}"

def google_drive_search(query: str) -> str:
    """(Placeholder) Searches for documents in Google Drive."""
    return f"Searching Google Drive for '{query}'... (This tool is not yet implemented)"


# --- Dynamic Tool Loading ---
TOOL_MAPPING = {
    "trello": trello_create_card,
    "browser": web_search,
    "google_drive": google_drive_search,
    "github": github_search,
}

enabled_tools = [
    TOOL_MAPPING[tool_name]
    for tool_name, settings in CONFIG["tools"].items()
    if settings.get("enabled") and tool_name in TOOL_MAPPING
]


# --- Model and Tools Configuration ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

with open("system_prompt.md", "r") as f:
    SYSTEM_PROMPT = f.read()

# Track which SDK is active
USE_NEW_GENAI: bool = False
client = None  # type: ignore[assignment]
model = None   # type: ignore[assignment]

try:
    # Prefer the new google-genai SDK if available
    from google import genai as new_genai  # type: ignore[import]
    from google.genai import types as genai_types  # type: ignore[import]

    if GEMINI_API_KEY:
        client = new_genai.Client(api_key=GEMINI_API_KEY)
    else:
        # Client can also pick up GEMINI_API_KEY from the environment
        client = new_genai.Client()

    USE_NEW_GENAI = True
except Exception:
    # Fallback to the legacy google.generativeai SDK
    legacy_genai.configure(api_key=GEMINI_API_KEY)

    model = legacy_genai.GenerativeModel(
        model_name=CONFIG["model"]["name"],
        generation_config={
            "temperature": CONFIG["model"]["temperature"],
            "max_output_tokens": CONFIG["model"]["max_tokens"],
        },
        tools=enabled_tools,
        system_instruction=SYSTEM_PROMPT,
    )

# --- Per-User Chat Session Management ---
chat_sessions: Dict[str, Any] = {}


def get_chat_session(user_id: str):
    """Retrieves or creates a chat session for a given user."""
    if user_id not in chat_sessions:
        if USE_NEW_GENAI and client is not None:
            # New google-genai SDK chat session
            from google.genai import types as genai_types  # type: ignore[import]

            chat_sessions[user_id] = client.chats.create(
                model=CONFIG["model"]["name"],
                config=genai_types.GenerateContentConfig(
                    temperature=CONFIG["model"]["temperature"],
                    max_output_tokens=CONFIG["model"]["max_tokens"],
                    tools=enabled_tools,
                    system_instruction=SYSTEM_PROMPT,
                ),
            )
        else:
            # Legacy google.generativeai chat session
            chat_sessions[user_id] = model.start_chat(history=[])
    return chat_sessions[user_id]


# --- Agent Logic ---
def agent(query: str, user_id: str) -> str:
    """
    The main agent logic. It sends the user's query to the Gemini model
    using a persistent, per-user chat session and handles the response.
    """
    start_time = datetime.utcnow()

    chat_session = get_chat_session(user_id)
    response = chat_session.send_message(query)

    final_response = response.text

    # Choose the appropriate way to read history based on SDK
    if USE_NEW_GENAI:
        history_messages = chat_session.get_history()
    else:
        history_messages = chat_session.history

    # Log the interaction
    log_entry = {
        "timestamp": start_time.isoformat(),
        "user_id": user_id,
        "query": query,
        "response": final_response,
        "history": [
            {
                "role": message.role,
                "parts": [part.text for part in message.parts],
            }
            for message in history_messages
        ],
        "feedback": None,
    }
    with open(LOG_FILE_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return final_response
