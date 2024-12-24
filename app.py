from flask import Flask, jsonify, request
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Update these with your actual values
# Replace with your actual values
GROUP_ID = '<GROUP_ID>'
REPORT_ID = '<REPORT_ID>'
TENANT_ID='<TENANT_ID>'
CLIENT_ID='<CLIENT_ID>',
CLIENT_SECRET='<CLIENT_SECRET>',

REPORT_EMBED_URL = f"https://app.powerbi.com/reportEmbed?reportId={REPORT_ID}&groupId={GROUP_ID}"

# Endpoint to get access token
def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://analysis.windows.net/powerbi/api/.default'
    }

    response = requests.post(url, headers=headers, data=data)
    token_data = response.json()
    
    if response.status_code != 200:
        raise Exception(f"Error fetching access token: {token_data.get('error_description')}")
    
    return token_data.get("access_token")

# Endpoint to generate embed token
@app.route('/get_embed_token', methods=['GET'])
def get_embed_token():
    try:
        access_token = get_access_token()
        
        embed_url = f"https://api.powerbi.com/v1.0/myorg/groups/{GROUP_ID}/reports/{REPORT_ID}/GenerateToken"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "accessLevel": "View",
            "allowSaveAs": True
        }

        response = requests.post(embed_url, headers=headers, json=data)
        embed_token_data = response.json()

        if response.status_code != 200:
            return jsonify({'error': embed_token_data.get('error', 'Unknown error')}), 400

        return jsonify({
            'accessToken': embed_token_data['token'],
            'embedUrl': REPORT_EMBED_URL,
            'reportId': REPORT_ID,
            'tokenId': embed_token_data['tokenId'],
            'expiration': embed_token_data['expiration']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)  # Run without SSL

