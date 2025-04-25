from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
LINE_CHANNEL_ACCESS_TOKEN = os.environ['LINE_CHANNEL_ACCESS_TOKEN']
MISTRAL_API_KEY = os.environ['MISTRAL_API_KEY']

@app.route('/webhook', methods=['POST'])
def webhook():
    event = request.json['events'][0]
    user_text = event['message']['text']
    
    # Call Mistral API
    response = requests.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "mistral-tiny",  # Or use "mistral-large-latest"
            "messages": [
                {"role": "user", "content": user_text}
            ]
        }
    )
    reply_text = response.json()['choices'][0]['message']['content']

    # Send back to LINE
    headers = {
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        "replyToken": event['replyToken'],
        "messages": [{"type": "text", "text": reply_text}]
    }
    requests.post('https://api.line.me/v2/bot/message/reply', headers=headers, json=data)

    return 'OK'

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
