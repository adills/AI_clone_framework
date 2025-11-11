# AI Thought-Partner Clone

This project is the foundational MVP of a personal AI assistant, designed to act as a "clone" of its user. It's built to understand your business, think in your style, and assist with tasks like content creation, research, and planning. This initial version focuses on providing a solid framework that can be extended with more tools and capabilities over time.

## Key Capabilities (MVP)

*   **Custom Persona:** The AI operates based on a `system_prompt.md` file, allowing you to define its voice, decision-making heuristics, and overall personality.
*   **Slack Integration:** Interact with your AI clone directly from your Slack workspace for a seamless workflow.
*   **Web Search:** The AI can perform real-time web searches to answer questions and research topics, providing up-to-date information.
*   **Extensible Toolset:** The architecture is built to support "tools." The `web_search`, `trello`, and `github` tools are fully functional. There is a non-functional placeholder for future integration with Google Drive.
*   **Data Logging:** All interactions are logged to `chat_logs.jsonl`, creating a valuable dataset for future fine-tuning and analysis.

## Environment Requirements

Before you can run the AI clone, you need to set up your environment variables. This project uses a `.env` file to manage sensitive API keys.

1.  **Create the `.env` file:** In the root of the project, create a file named `.env`.
2.  **Add the following keys:** You will need to get API keys from the following services:

    ```
    GEMINI_API_KEY="your_google_ai_gemini_api_key_here"
    SLACK_BOT_TOKEN="your_slack_bot_token_here_xoxb-..."
    SLACK_SIGNING_SECRET="your_slack_app_signing_secret_here"
    SLACK_APP_TOKEN="your_slack_app_level_token_here_xapp-..."
    SERPAPI_API_KEY="your_serpapi_api_key_here"
    TRELLO_API_KEY="your_trello_api_key_here"
    TRELLO_API_TOKEN="your_trello_api_token_here"
    ```

    *   **GEMINI\_API\_KEY:** Get this from [Google AI Studio](https://aistudio.google.com/apikey).
    *   **SLACK\_\*\_TOKEN/SECRET:** You'll need to create a new Slack App. Follow the [Slack Bolt for Python documentation](https://docs.slack.dev/tools/bolt-python/getting-started) to set up your app and get the necessary tokens. You will need to enable Socket Mode for your app.
    *   **SERPAPI\_API\_KEY:** Get this from the [SerpApi website](https://serpapi.com/) to enable the web search tool.
    *   **TRELLO\_API\_KEY/TOKEN:** You can get your Trello API key and generate a token by following the instructions at [Trello's API documentation](https://developer.atlassian.com/cloud/trello/guides/rest-api/authorization/). You will also need to specify the Trello List ID in the `config.yaml` file where you want the AI to create cards.
    *   **GITHUB\_TOKEN:** You can generate a personal access token by following the instructions in the [GitHub documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token). The token will need the `public_repo` scope to search public repositories.

## Installation Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```
2.  **Create a virtual environment (recommended) and install dependencies:**

    Option 1:
    
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

    Option 2 (pipenv):
    
    ```bash
    pipenv --python 3.11
    pipenv install -r requirements.txt
    ```

## Operating Instructions

1.  **Ensure your `.env` file is correctly configured** with all the required API keys.
2.  **Start the Slack bot:**
    ```bash
    python slack_bot.py
    ```
3.  **Interact with your AI Clone:** Once the bot is running, you can go to your Slack workspace and send messages to it in the channel you configured during the Slack app setup.

## Training Your AI Clone

This MVP is designed to learn from your feedback over time. Here’s how you can contribute to its training:

*   **Interaction Logging:** Every conversation you have with the bot is automatically saved to the `logs/chat_logs.jsonl` file. This data is the foundation for any future fine-tuning.
*   **Manual Feedback (Future):** While not yet implemented, the logging schema includes a `feedback` field. In the future, you'll be able to provide explicit feedback (e.g., with emoji reactions in Slack) to mark good and bad responses.
*   **Editing the Persona:** The easiest way to train the AI right now is to refine the `system_prompt.md` file. If you find the AI is not responding in the way you'd like, you can adjust its persona, voice, and decision-making rules in this file.

## Future Enhancements

This project is just getting started. Here is a roadmap of planned features:

*   **Implement Core Tools:**
    *   **Google Drive Search:** Connect to Google Drive to allow the AI to search your documents for context.
    *   **Trello Integration: DONE** Give the AI the ability to create and manage Trello cards for tasks and ideas.
    *   **GitHub Search: DONE** Enable the AI to search for code repositories and libraries on GitHub.
*   **Improved Memory:** Develop a more sophisticated long-term memory system for the AI, allowing it to remember key facts and preferences from your conversations.
*   **Fine-Tuning:** Use the logged data to fine-tune a base model, creating a version of the AI that more accurately reflects your unique style and judgment.
*   **Web Interface:** Build a simple web-based chat interface as an alternative to the Slack bot.

We welcome contributions and suggestions! Please feel free to open an issue or submit a pull request.
