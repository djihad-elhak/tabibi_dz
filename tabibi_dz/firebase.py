import firebase_admin
from firebase_admin import credentials

def initialize_firebase():
    cred = credentials.Certificate('firebase_service_account.json')
    firebase_admin.initialize_app(cred)

# Call the function to initialize Firebase in your settings or views
initialize_firebase()
