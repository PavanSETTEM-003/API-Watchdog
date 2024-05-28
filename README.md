# API-Watchdog

## Project Overview

API-Watchdog is a tool designed to monitor and capture the run times of API calls, specifically integrated with the UPstox API. This project automates the process of handling API access codes and ensures efficient performance monitoring during trading hours.

### Key Features

- **UPstox API Integration:** Seamlessly connected to the UPstox API, requiring an access code for operation.
- **Telegram Bot Integration:** Utilizes a Telegram bot to handle access code expirations. When the access code expires, the bot sends a notification. Users can then provide the new access code via the chat, which is subsequently updated in the MongoDB database.
- **Automated Monitoring:** During trading hours, API-Watchdog sends API calls every minute and captures their run times.
- **Cloud-Based:** All configurations and data are stored and monitored in MongoDB Cloud for easy access and management.

### Setup and Run Instructions

To set up and run the project locally, follow the steps below:

1. **Clone this repository and navigate to the cloned repository:**

    ```bash
    git clone https://github.com/PavanSETTEM-003/API-Watchdog.git
    cd API-Watchdog
    ```

2. **Create a virtual environment and activate it:**

    ```bash
    python -m venv virtualenv
    ```

    On Windows:
    ```bash
    .\virtualenv\Scripts\activate
    ```

    On macOS/Linux:
    ```bash
    source virtualenv/bin/activate
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Populate the Configuration Details:**

    Create a `.env` file in the root directory of the project and populate it with the following configuration details:

    ```env
    # Database Setup
    mongodb_connection_string = "<your_mongodb_connection_string>"
    DB_NAME = "<your_db_name>"
    Config_collection_name = "<your_config_collection_name>"
    Response_time_collection_name = "<your_response_time_collection_name>"

    # Telegram BOT access Tokens
    BOT_ID = "<your_bot_id>"
    CHAT_ID = "<your_chat_id>"
    ```

    Please watch the YouTube video for creating a Telegram bot:
    [How to Create a Telegram Bot](https://youtu.be/UQrcOj63S2o?si=3ExwmF05xZiqfRTN)

    To get the chat ID, run the following code:

    ```python
    import requests

    # Replace with your actual token (avoid exposing it in code)
    TOKEN = "<your_bot_token>"

    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset=0"
    response = requests.get(url).json()

    # Check if any updates are present
    if not response['result']:
        print("Send one more message to the BOT")

    last_message = response['result'][0]
    print(last_message)
    ```

5. **Database Configuration:**

    This project requires several configuration settings to be stored in the database, which can be updated as needed without modifying the `.env` file directly. These configurations include the UPstox API details and are stored in the `Config_collection_name` in your MongoDB database. An example document in the `Config_collection_name` might look like this:

    ```json
    {
      "_id": {
        "$oid": "663fb6612f3e3ae4a88e6f85"
      },
      "Description": "Config_doc",
      "Access_code": "",
      "API_KEY": "",
      "SECRET_KEY": "",
      "REDIRECT_URL": ""
    }
    ```

    **Update the required fields:**
    - Modify the `Access_code`, `API_KEY`, `SECRET_KEY`, and `REDIRECT_URL` fields as necessary.
    - Ensure the document structure remains consistent with the example provided above.

6. **Run the Python file:**

    ```bash
    python main.py
    ```

