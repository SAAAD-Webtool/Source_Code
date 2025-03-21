from flask import Flask, request, jsonify, render_template, send_file
import pandas as pd
import smtplib
import os

app = Flask(__name__, template_folder='templates')

df = pd.read_excel("SAAAD/descriptions.xlsx", engine='openpyxl')
image_base_dir = ("static/compund images")


def get_image_path(compund_name):

    image_path = os.path.join(image_base_dir, f"{compund_name}.png")
    if os.path.exists(image_path):
        return image_path
    return None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('query')
    if not query:
        return jsonify({'suggestions': []})

    query = query.strip().lower()

    suggestions = df[df['Sialic acid analogues'].str.contains(query,
                                                              case=False,
                                                              na=False,
                                                              regex=False)]

    suggestions_list = suggestions['Sialic acid analogues'].tolist()

    return jsonify({'suggestions': suggestions_list})


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    if not query:
        return jsonify({'results': [], 'suggestions': []})

    print(f"Search Query: {query}")

    query = query.strip().lower()

    try:
        results = df[df['Sialic acid analogues'].str.contains(query,
                                                              case=False,
                                                              na=False,
                                                              regex=False)]
    except Exception as e:
        return str({'error': f'Error processing the search: {str(e)}'}), 400, {
            'ContentType': 'application/json'
        }

    if results.empty:
        return jsonify({'results': [], 'suggestions': []})

    results_dict = results.fillna('').astype(object).to_dict(orient='records')
    print(f"Results Dict: {results_dict}")

    for result in results_dict:
        for key, value in result.items():
            if pd.isna(value):
                print(f"NaN value found in results_dict: {key} = {value}")
                result[key] = None

    for result in results_dict:
        result['Image'] = get_image_path(result['Sialic acid analogues'])

    suggestions = [result['Sialic acid analogues'] for result in results_dict]
    print(f"Suggestions: {suggestions}")

    return jsonify({'results': results_dict, 'suggestions': suggestions})


@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join("SAAAD/sialic acid analog", filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    return send_file(file_path, as_attachment=True)


SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'saaad2k25@gmail.com'
SMTP_PASSWORD = 'xxxxx'


@app.route('/submit_question', methods=['POST'])
def ask_question():
    user_email = request.form['email']  
    question = request.form['user_question'] 

    send_email(user_email, question)  

    return jsonify({'message': 'Question sent successfully!'})

def send_email(user_email, question):  
    from_email = SMTP_USERNAME
    to_email = 'saaad2k25@gmail.com'
    subject = 'New Question from User'

    body = f"""You have received a new question:

From: {user_email}

Question:
{question}
"""

    email_message = f'Subject: {subject}\n\n{body}'

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(from_email, to_email, email_message)



if __name__ == '__main__':
    print("App is starting...")
    app.run(host='0.0.0.0', port=8080, debug=True)
