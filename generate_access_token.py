import os
import json
import requests
from urllib.parse import quote

URL = "https://auth.eagleeyenetworks.com/oauth2/token"

def get_required_data():
    required_data = {}
    
    required_data['refresh_token'] = input("Enter your refresh token: ")
    required_data['scope'] = 'vms.all'
    required_data['token_type'] = 'Bearer'
    required_data['cc_base64'] = input("Enter your clientId:clientSecret base64 encoded: ")
    
    return required_data

def get_filepath(filename):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, filename)

def read_json(filename):
    with open(get_filepath(filename), 'r') as f:
        return json.load(f)

def write_json(filename, data):
    with open(get_filepath(filename), 'w') as f:
        json.dump(data, f, indent=4)

def make_request(url, headers, data):
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        if response:
            print(f"Status Code: {response.status_code}, Reason: {response.reason}")
        raise

def main():
    required_data = get_required_data()

    headers = {
        "Accept": "application/json",
        "Authorization": f"Basic {required_data['cc_base64']}"
    }

    data = {
        "grant_type": "refresh_token",
        "refresh_token": quote(required_data['refresh_token'])
    }

    new_access_data = make_request(URL, headers, data)
    write_json('access_token.json', new_access_data["access_token"])

    print(f"Request URL: {URL}\n")
    print("Headers:")
    print(json.dumps(headers, indent=4))
    print("Data:")
    print(json.dumps(data, indent=4))
    print("\nSuccessfully updated access token.\n")
    print(f"Access_token: {new_access_data['access_token']}\n")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    clear_terminal()
    main()
