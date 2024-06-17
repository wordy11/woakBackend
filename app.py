from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import mimetypes


app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "*"}})

@app.route('/chat_bot', methods=['POST'])
def chat_bot():
    # Extract sender and message from the JSON POST body
    data = request.get_json()
    sender = data.get('sender')
    message = data.get('message')
    
    if not sender or not message:
        return jsonify({"status": "error", "message": "Missing sender or message"}), 400
    
    url = 'https://woakbot.woakconstruction.com/webhooks/rest/webhook'
    headers = {'Content-Type': 'application/json'}
    data_to_send = {
        "sender": sender,
        "message": message
    }
    
    try:
        response = requests.post(url, json=data_to_send, headers=headers)
        response.raise_for_status()
        return jsonify({"status": "success", "response": response.json()}), 200
    except requests.exceptions.RequestException as err:
        return jsonify({"status": "error", "message": str(err)}), 500


def send_plain_text_email(recipient_email, body, subject):
    sender_email = "sascente00@gmail.com"
    password = "kbgi ssed nwlf txmr"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender_email, password)
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())

@app.route('/send_contact_email', methods=['POST'])
def send_email_endpoint():
    # Extract data from the POST request
    data = request.get_json()
    subject = data.get('subject')
    body = data.get('body')
    recieve = "support@woakconstruction.com"
    
    # Validate required fields
    if not all([subject, body]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400
    
    # Call the send_plain_text_email function
    try:
        send_plain_text_email(recieve, body, subject)
        return jsonify({"status": "success", "message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    

def send_email_with_attachment_and_text(recipient_email, subject, body, attachment, cv):
    sender_email = "sascente00@gmail.com"
    password = "kbgi ssed nwlf txmr"
    # Create multipart message and set headers
    message = MIMEMultipart('related')
    message['Subject'] = subject
    message['From'] = sender_email
    message['To'] = recipient_email

    # Attach plain text and HTML version of your message
    part1 = MIMEText(body, 'plain')
    # part2 = MIMEText(body, 'html')

    # Attach the plain text and HTML version to the email
    message.attach(part1)
    # message.attach(part2)
    
    # Convert file storage objects to MIMEBase instances
    attachment_part = MIMEBase(attachment.content_type.split('/')[0], attachment.content_type)
    attachment_part.set_payload(attachment.read())
    encoders.encode_base64(attachment_part)
    attachment_part.add_header('Content-Disposition', f'attachment; filename="resume: {attachment.filename}"')
    message.attach(attachment_part)
    
    if cv is not None:
        # Use the content_type attribute of the FileStorage object to set the MIME type for the CV
        cv_part = MIMEBase(cv.content_type.split('/')[0], cv.content_type)
        cv_part.set_payload(cv.read())
        encoders.encode_base64(cv_part)
        cv_part.add_header('Content-Disposition', f'attachment; filename="cv: {cv.filename}"')
        message.attach(cv_part)

    # Connect to the server and send the email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient_email, message.as_string())

@app.route('/send_email_with_attachment', methods=['POST'])
def send_email_with_attachment_endpoint():
    # Extract data from the form
    recipient_email = "career@woakconstruction.com"
    subject = request.form.get('subject')
    body = request.form.get('body')
    attachment_file = request.files.get('resume')
    if attachment_file is None:
        # No file was passed or the file is empty
        return jsonify({"status": "error", "message": "All fields are required except cv path"}), 400
    cv_file = request.files.get('cv')
    
    # Validate required fields
    if not all([subject, body]) and not attachment_file:
        return jsonify({"status": "error", "message": "All fields are required except cv path"}), 400

    
    # Call the send_email_with_attachment_and_text function
    try:
        # send_email_with_attachment_and_text(recipient_email, subject, body, attachment_file, cv_file)
        return jsonify({"status": "success", "message": "Email with attachment sent successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)