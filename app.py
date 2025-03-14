import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

ADO_ORG = os.getenv('ADO_ORG')
ADO_PAT = os.getenv('ADO_PAT')
ADO_PROJECT = os.getenv('ADO_PROJECT')
USER_STORY_ID = 13991

@app.route('/create-task', methods=['POST'])
def create_task():
    data = request.form
    
    # Verify Slack token (if needed)
    token = data.get('token')
    
    # Parse Slack message
    message_text = data.get('text', '')
    title, description = (message_text.split('|', 1) + [None])[:2]
    
    if not title:
        return jsonify({"error": "Task title is required."}), 400

    # Create task in ADO
    url = f'https://dev.azure.com/{ADO_ORG}/{ADO_PROJECT}/_apis/wit/workitems/$task?api-version=7.1-preview.3'
    headers = {
        'Content-Type': 'application/json-patch+json',
        'Authorization': f'Basic {ADO_PAT}'
    }

    payload = [
        {"op": "add", "path": "/fields/System.Title", "value": title.strip()},
        {"op": "add", "path": "/fields/System.Description", "value": description.strip() if description else ""},
        {"op": "add", "path": "/fields/System.WorkItemType", "value": "Task"},
        {"op": "add", "path": "/fields/System.IterationPath", "value": f"{ADO_PROJECT}"},
        {"op": "add", "path": "/fields/System.Parent", "value": USER_STORY_ID}
    ]

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return jsonify({"message": "Task created successfully in Azure DevOps."})
    else:
        return jsonify({"error": "Failed to create task in Azure DevOps.", "details": response.json()}), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
