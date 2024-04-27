import os
from google.oauth2 import service_account
from googleapiclient.discovery import build, Resource
from googleapiclient.http import MediaFileUpload
import dotenv

dotenv.load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.environ.get("SERVICE_ACCOUNT_FILE")
GDRIVE_FOLDER_ID = os.environ.get("GDRIVE_FOLDER_ID")

credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def create_service():
    return build("drive", "v3", credentials=credentials)


drive_service: Resource = create_service()


def create_folder(folder_name, drive_service: Resource=drive_service):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = drive_service.files().create(body=file_metadata, fields='id').execute()

    return folder.get('id')

def create_file(file_name, local_file, folder_id=GDRIVE_FOLDER_ID, drive_service=None):
    if not drive_service:
        drive_service = create_service()

    file_metadata = {
        'name': file_name,
        'parents': [folder_id],
        'mimeType': 'text/plain'
    }
    media = drive_service.files().create(body=file_metadata, media_body=MediaFileUpload(local_file, mimetype="text/plain") ).execute()

    Id = media.get('id')

    perms = {
        'role': 'reader',
        'type': 'anyone'
    }

    drive_service.permissions().create(fileId=Id, body=perms).execute()

    download_url = f"https://drive.google.com/uc?export=view&id={Id}"

    return download_url

def get_file(file_id, drive_service=None):
    if not drive_service:
        drive_service = create_service()

    content = drive_service.files().get_media(fileId=file_id).execute()
    return content

def delete_file(file_id, drive_service=drive_service):
    drive_service.files().delete(fileId=file_id).execute()

