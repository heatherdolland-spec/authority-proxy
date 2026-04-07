from flask import Flask, request, jsonify
import anthropic
import os

app = Flask(__name__)

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, HEAD, POST, OPTIONS'
    return response

@app.route('/', methods=['GET', 'HEAD', 'OPTIONS', 'POST'])
def proxy():
    if request.method in ['GET', 'HEAD']:
        return jsonify({'status': 'Authority Proxy Running'})

    if request.method == 'OPTIONS':
        return jsonify({})

    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    data = request.json

    message = client.messages.create(
        model=data['model'],
        max_tokens=data['max_tokens'],
        system=data['system'],
        messages=data['messages']
    )

    return jsonify({
        'content': [{'text': message.content[0].text, 'type': 'text'}]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
