import os
import pickle
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive']
auth_flows = {}

TOKEN_PATH = os.path.join(os.path.dirname(__file__), 'token.pickle')


def get_auth_url_and_flow():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        SCOPES,
        redirect_uri='http://localhost:8092/oauth_callback'
    )
    auth_url, state = flow.authorization_url(prompt='consent')
    return auth_url, state, flow



def save_token(creds):
    with open(TOKEN_PATH, 'wb') as token:
        pickle.dump(creds, token)


def load_credentials():
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
            if creds and creds.valid:
                return creds
            elif creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                save_token(creds)
                return creds
    return None


def build_service():
    creds = load_credentials()
    return build('drive', 'v3', credentials=creds)


def list_drive_folders(service):
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.folder' and trashed=false",
        spaces='drive',
        fields="files(id, name)").execute()
    return results.get('files', [])


def upload_file_to_drive(service, file_path, file_name, mime_type, folder_id=None):
    metadata = {'name': file_name}
    if folder_id:
        metadata['parents'] = [folder_id]

    media = MediaFileUpload(file_path, mimetype=mime_type)
    file = service.files().create(
        body=metadata,
        media_body=media,
        fields='id').execute()
    return file.get('id')