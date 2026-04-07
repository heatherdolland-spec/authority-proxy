from flask import Flask, request, jsonify
import anthropic
import os

app = Flask(__name__)

@app.route('/', methods=['OPTIONS', 'POST'])
def proxy():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        return response

    client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    data = request.json
    
    message = client.messages.create(
        model=data['model'],
        max_tokens=data['max_tokens'],
        system=data['system'],
        messages=data['messages']
    )
    
    response = jsonify({
        'content': [{'text': message.content[0].text, 'type': 'text'}]
    })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
