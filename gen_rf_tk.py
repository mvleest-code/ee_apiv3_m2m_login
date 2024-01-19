import json, requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Constants
HOST_NAME = "127.0.0.1"
PORT = 3333
CLIENT_ID = input("Enter your client ID: ")
CLIENT_SECRET = input("Enter your client secret: ")
AUTH_URL = "https://auth.eagleeyenetworks.com"
BASE_URL = "https://api.eagleeyenetworks.com"

# Utility Functions
def make_request(method, url, headers=None, auth=None):
    response = requests.request(method, url, headers=headers, auth=auth)
    if response.status_code == 200:
        return json.loads(response.text)
    else:
        return None

# OAuth and User Details Handling
def get_tokens(code):
    url = f"{AUTH_URL}/oauth2/token?grant_type=authorization_code&scope=vms.all&code={code}&redirect_uri=http://{HOST_NAME}:{PORT}"
    return make_request("POST", url, auth=(CLIENT_ID, CLIENT_SECRET))

def get_base_url(accessToken):
    url = f"{BASE_URL}/api/v3.0/clientSettings"
    headers = {"accept": "application/json", "authorization": f"Bearer {accessToken}"}
    settings = make_request("GET", url, headers=headers)
    return settings.get('httpsBaseUrl', {}).get('hostname') if settings else None

def get_user_details(accessToken, base_url):
    url = f"https://{base_url}/api/v3.0/users/self"
    headers = {"accept": "application/json", "authorization": f"Bearer {accessToken}"}
    return make_request("GET", url, headers=headers)

# Route Handlers
@app.route('/')
def index():
    code = request.args.get('code')
    if code:
        oauthObject = get_tokens(code)
        accessToken = oauthObject.get('access_token') if oauthObject else None
        base_url = get_base_url(accessToken) if accessToken else None
        userDetails = get_user_details(accessToken, base_url) if base_url else None
        userId = userDetails.get('id', 'unknown') if userDetails else 'unknown'
        refresh_token = oauthObject.get('refresh_token', 'unknown') if oauthObject else 'unknown'
        
        with open('access_response.json', 'w') as f:
            json.dump(oauthObject, f) if oauthObject else None

        return render_template_string(LOGIN_TEMPLATE, userId=userId, refresh_token=refresh_token)
    else:
        endpoint = f"{AUTH_URL}/oauth2/authorize?client_id={CLIENT_ID}&response_type=code&scope=vms.all&redirect_uri=http://{HOST_NAME}:{PORT}"
        return render_template_string(LOGIN_LINK_TEMPLATE, endpoint=endpoint)

# HTML Templates with Bootstrap
LOGIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login Success</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Eagle Eye Networks Login</h1>
        <div class="alert alert-success" role="alert">
            You are logged in. Your user ID is {{ userId }}.
        </div>
        <div class="form-group">
            <label for="refreshToken">Refresh Token:</label>
            <input type="text" class="form-control" id="refreshToken" value="{{ refresh_token }}" readonly>
        </div>
        <button class="btn btn-primary" onclick="copyToClipboard()">COPY</button>
        <script>
        function copyToClipboard() {
            var copyText = document.getElementById("refreshToken");
            copyText.select();
            document.execCommand("copy");
        }
        </script>
    </div>
</body>
</html>
'''

LOGIN_LINK_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container mt-5">
        <h1 class="text-center">Eagle Eye Networks Login</h1>
        <p class="text-center">Please click the link below to generate a refresh token.</p>
        <div class="text-center">
            <a href="{{ endpoint }}" class="btn btn-primary">Login</a>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host=HOST_NAME, port=PORT)
