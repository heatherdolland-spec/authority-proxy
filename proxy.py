from flask import Flask, request, jsonify
import anthropic
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

def send_email(to_email, subject, body, reply_to=None):
    try:
        smtp_user = os.environ.get('EMAIL_USER')
        smtp_pass = os.environ.get('EMAIL_PASS')
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = to_email
        msg['Subject'] = subject
        if reply_to:
            msg['Reply-To'] = reply_to
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print('Email error:', e)
        return False

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
    data = request.json
    if data.get('type') == 'email':
        success = send_email(
            data.get('to'),
            data.get('subject'),
            data.get('body'),
            data.get('reply_to')
        )
        return jsonify({'status': 'sent' if success else 'failed'})
    try:
        client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        extra = {}
        if data.get('output_config'):
            extra['output_config'] = data['output_config']
        message = client.messages.create(
            model=data['model'],
            max_tokens=data['max_tokens'],
            system=data['system'],
            messages=data['messages'],
            extra_body=extra or None
        )
        # Newer models can return thinking blocks before the text, so keep only the text
        text = ''.join(b.text for b in message.content if b.type == 'text')
        return jsonify({
            'content': [{'text': text, 'type': 'text'}]
        })
    except Exception as e:
        print('Claude API error:', e)
        return jsonify({'error': {'message': str(e)}}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
