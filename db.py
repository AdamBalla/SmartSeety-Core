import pyrebase
from config import FIREBASE_DATABASE_URL, FIREBASE_API_KEY, FIREBASE_AUTH_URL, FIREBASE_STORAGE_URL, FIREBASE_SERVICE_ACCOUNT_PATH

firebase = pyrebase.initialize_app({
    'databaseURL': FIREBASE_DATABASE_URL,
    'authDomain': FIREBASE_AUTH_URL,
    'apiKey': FIREBASE_API_KEY,
    'storageBucket': FIREBASE_STORAGE_URL,
    'serviceAccount': FIREBASE_SERVICE_ACCOUNT_PATH
    })

DB = firebase.database()