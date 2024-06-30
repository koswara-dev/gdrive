import os
import io
import sys

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')

# Service Account Credentials
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def get_drive_service():
    return build('drive', 'v3', credentials=credentials)


def list_files_and_folders(service):
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files and folders:')
        for item in items:
            print(f'{item["name"]} ({item["id"]})')


def create_folder(service, folder_name):
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    file = service.files().create(body=file_metadata, fields='id').execute()
    print(f'Folder ID: {file.get("id")}')


def upload_file(service, file_path, file_name, folder_id=None):
    file_metadata = {'name': file_name}
    if folder_id:
        file_metadata['parents'] = [folder_id]
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'File ID: {file.get("id")}')


def download_file(service, file_id, file_name):
    request = service.files().get_media(fileId=file_id)
    fh = io.FileIO(file_name, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f'Download {int(status.progress() * 100)}%.')


def delete_file_or_folder(service, file_id):
    service.files().delete(fileId=file_id).execute()
    print('File or folder deleted successfully')


def rename_file_or_folder(service, file_id, new_name):
    file_metadata = {'name': new_name}
    service.files().update(fileId=file_id, body=file_metadata, fields='name').execute()
    print(f'File or folder renamed to: {new_name}')


def check_drive_free_space(service):
    about = service.about().get(fields="storageQuota").execute()
    quota = about.get('storageQuota')
    if quota:
        limit = int(quota['limit'])
        usage = int(quota['usage'])
        free_space = limit - usage

        print(f"Total space: {limit / (1024*1024*1024):.2f} GB")
        print(f"Used space: {usage / (1024*1024*1024):.2f} GB")
        print(f"Free space: {free_space / (1024*1024*1024):.2f} GB")
    else:
        print("Unable to retrieve storage information.")


def main():
    drive_service = get_drive_service()
    
    while True:
        print("\nGoogle Drive File Management:\n")
        print("1. List files and folders")
        print("2. Create new folder")
        print("3. Upload file")
        print("4. Download file")
        print("5. Delete file or folder")
        print("6. Rename file or folder")
        print("7. Check drive free space")
        print("0. Exit program")
        
        choice = input("Enter your choice: ")

        if choice == '0':
            print("Exiting program.")
            sys.exit(0)
        elif choice == '1':
            list_files_and_folders(drive_service)
        elif choice == '2':
            folder_name = input("Enter the name of the folder to create: ")
            create_folder(drive_service, folder_name)
        elif choice == '3':
            file_path = input("Enter the path of the file to upload: ")
            file_name = input("Enter the name to save the uploaded file as on Google Drive: ")
            folder_id = input("Enter the folder ID to upload into (optional): ")
            folder_id = folder_id if folder_id else None
            upload_file(drive_service, file_path, file_name, folder_id)
        elif choice == '4':
            file_id = input("Enter the file ID to download: ")
            file_name = input("Enter the name to save the downloaded file as: ")
            download_file(drive_service, file_id, file_name)
        elif choice == '5':
            file_id = input("Enter the file or folder ID to delete: ")
            delete_file_or_folder(drive_service, file_id)
        elif choice == '6':
            file_id = input("Enter the file or folder ID to rename: ")
            new_name = input("Enter the new name: ")
            rename_file_or_folder(drive_service, file_id, new_name)
        elif choice == '7':
            check_drive_free_space(drive_service)
        else:
            print("Invalid choice. Please try again.")


if __name__ == '__main__':
    main()
