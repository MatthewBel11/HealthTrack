from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials
import dotenv
import joblib
import numpy as np
from flask import request, jsonify
import os

app = Flask(__name__)

# Replace with environment variable or secure storage for the secret key
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')

# Configuration for file uploads
UPLOAD_FOLDER = 'static/documents'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

# Load Firebase credentials from environment or a secure file
cred = credentials.Certificate({
    "type": "service_account",
    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),  # To handle line breaks in env
    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_CERT_URL')
})

firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL')
})

# Load models and scalers (uncomment after adding the actual paths)
# model_maternal = joblib.load('models/maternal_mortality_model.pkl')
# model_infant = joblib.load('models/infant_mortality_model.pkl')

# scaler_maternal = joblib.load('pred_model/scaler_3.1.pkl')
# scaler_infant = joblib.load('pred_model/scaler_3.2.pkl')

@app.route("/")
def hello_world():
    return render_template("home.html")

# Blueprint registration (example)
from auth.views import auth_blueprint
from account.views import account_blueprint

app.register_blueprint(auth_blueprint)
app.register_blueprint(account_blueprint)

if __name__ == "__main__":
    app.run()

# Load secret keys and database configurations securely
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Recaptcha keys should also be in environment variables
app.config['RECAPTCHA_PUBLIC_KEY'] = os.getenv('RECAPTCHA_PUBLIC_KEY')
app.config['RECAPTCHA_PRIVATE_KEY'] = os.getenv('RECAPTCHA_PRIVATE_KEY')

# For any database private key, make sure to load it securely
DB_PRIVATE_KEY = os.getenv('DB_PRIVATE_KEY').replace('\\n', '\n')
DB_KEY_ID = os.getenv('DB_KEY_ID')
