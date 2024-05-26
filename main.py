import requests
import datetime
import time
import pytz
import logging

from pymongo import MongoClient
from dotenv import dotenv_values

config = dotenv_values(".env")

# Define start and end times for the desired time range (8:30 to 15:30 IST)
start_time = datetime.time(8, 29)
end_time = datetime.time(16, 1)
timer = 60.0

logging.basicConfig(level=logging.INFO)

def IST(message):
    return f"{datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')} -- {message}"

# Configuring Database
mongodb_client = MongoClient(config["mongodb_connection_string"])
database = mongodb_client[config["DB_NAME"]]
Response_time_collection = database[config["Response_time_collection_name"]]
Config_collection = database[config["Config_collection_name"]]

matching_document = Config_collection.find_one({"Description": "Config_doc"})

#Configuring Telegram Bot
BOT_TOKEN = config["BOT_ID"]
CHAT_ID = config["CHAT_ID"]

url = 'https://api-v2.upstox.com/login/authorization/token'
headers = {
    'accept': 'application/json',
    'Api-Version': '2.0',
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'code': matching_document["Access_code"],
    'client_id': matching_document["API_KEY"],
    'client_secret': matching_document["SECRET_KEY"],
    'redirect_uri': matching_document["REDIRECT_URL"],
    'grant_type': 'authorization_code'
}

def is_between(start_time, end_time):
    """Check if the current time is between start_time and end_time."""
    now = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).time()
    return start_time <= now <= end_time

def send(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage?chat_id={CHAT_ID}&text={message}"
        response = requests.get(url).json() # this sends the message

        return True

    except Exception as error:

        return False

def get_code_tele():

    try:
        # fetch the previous access_code
        past_access_code = Config_collection.find_one({"Description": "Config_doc"})["Access_code"]

        while True:

            tele_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset=-1"
            response = requests.get(tele_url).json()

            # Check if any updates are present
            if response['result']:
                
                last_message = response['result'][0]
                # print(last_message)

                access_code_url = last_message["message"]["text"]
                access_code = access_code_url.split('=')[-1]

                if access_code_url and ("https://127.0.0.1:3000/?code=" in access_code_url and past_access_code != access_code):
                    
                    current_time = datetime.datetime.now()

                    Config_collection.update_one(
                        { "Access_code": { "$exists": True } }, # Filter criteria
                        { "$set": { "Access_code": access_code } } # Update operation
                        )
                    
                    send("🟢 Token updated successfully")

                    logging.info(IST("Access code changed"))

                    return True
            
            else:
                logging.warning(IST("unable to get the updated message from telegram bot"))
            
    except Exception as error:
        # Log the error properly
        send(f"Tele_func \n :{error}")
        logging.error(IST(error))

        return False

def process_access_code(url, headers, data):
    logging.info(IST("Triggered"))
    try:
        if 'code' in data:
            data['code'] = Config_collection.find_one({"Description": "Config_doc"})["Access_code"] # updating the access code

        response = requests.post(url, headers=headers, data=data)
        json_response = response.json()
        access_token = json_response.get("access_token")

        # print(json_response)

        if "errors" in json_response and json_response["errors"][0]['message'] == 'Invalid Auth code':
            send("⚠ Alert : Access Code Expired")

            past_access_code = Config_collection.find_one({"Description": "Config_doc"})["Access_code"]

            while True:
                get_code_tele()
                if(past_access_code == Config_collection.find_one({"Description": "Config_doc"})["Access_code"]):
                   print("not updated")
                   time.sleep(60)
                else:
                    # After updating the access code gets updated
                    process_access_code_response, access_token = process_access_code(url, headers, data)
                    if(process_access_code_response):
                        return process_access_code_response, access_token

        elif access_token is None:
            send(json_response)

            return False, None

        else:
            return True, access_token

    except Exception as error:
        logging.error(IST(error))
        send(f"process_access_code : \n{error}")

        return False, None
    

def get_access_token():
    process_access_code_response, access_token = process_access_code(url, headers, data)

    if(process_access_code_response):
        return access_token
    
    return False


def response_time_tracking(access_token):
    try:
        
        profile_url = "https://api.upstox.com/v2/user/profile"
        profile_headers = {
            "Accept": "application/json",
            "Authorization": "Bearer {}".format(access_token),
        }

        start_time = time.time()  # Record the start time

        response = requests.get(profile_url, headers=profile_headers)

        # print(response)
        
        end_time = time.time()  # Record the end time
        response_time = end_time - start_time  # Calculate the response time

        # Get current IST time
        IST_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))

        # Desired timestamp format (same as in response_data)
        desired_format = "%Y-%m-%d %H:%M:%S"

        #print(f"{IST_time.strftime(desired_format)} >> Inserted")

        # Format timestamps directly in IST
        response_data = {
            "timestamp": IST_time.strftime(desired_format),
            "response_time": response_time,

        }

        Response_time_collection.insert_one(response_data)

        return True
                

    except Exception as error:
        send(f"response_time_tracking : \n{error}")
        logging.error(IST(error))

        return False
    
def main_code():
    
    access_token = get_access_token()

    if(access_token):

        logging.info(IST("Tracking started"))
        send("▶️ Tracking Started")
        starttime = time.monotonic()
        while True:
            
            response_time_tracking(access_token)
            time.sleep(timer - ((time.monotonic() - starttime) % timer))

            if not is_between(start_time, end_time):
                logging.info(IST("Tracking Stopped"))
                send("⏸ Tracking Stopped")
                time.sleep(16*60*60)
                break


    else:
        send("Unable to generate Access Token")

logging.info(IST("Deployment successful 🚀"))

while True:
    # Check if the current time is within the desired range
    if is_between(start_time, end_time):
        main_code()
