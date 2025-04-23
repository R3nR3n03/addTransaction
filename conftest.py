import requests

# API endpoint
auth_url = "http://192.168.202.110:443/Login"

# Headers with required DeviceName
headers = {
    "DeviceName": "ActiveSystemsTablet"
}
# Send request with headers
response = requests.post(auth_url, auth=("Admin", "1"), headers=headers)


# Check if authentication is successful
if response.status_code == 200:
    token = response.json().get("access_token")
    print("Response JSON:", response.json())

else:
    print("Error:", response.status_code, response.text)
