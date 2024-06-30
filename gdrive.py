import os
import io
import argparse

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


def main(args):
    drive_service = get_drive_service()

    if args.command == 'list':
        list_files_and_folders(drive_service)
    elif args.command == 'create-folder':
        create_folder(drive_service, args.name)
    elif args.command == 'upload':
        upload_file(drive_service, args.path, args.name, args.folder_id)
    elif args.command == 'download':
        download_file(drive_service, args.file_id, args.name)
    elif args.command == 'delete':
        delete_file_or_folder(drive_service, args.file_id)
    elif args.command == 'rename':
        rename_file_or_folder(drive_service, args.file_id, args.new_name)
    elif args.command == 'drive-usage':
        check_drive_free_space(drive_service)
    else:
        print("Unknown command. Please use a valid command.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Google Drive File Management')
    subparsers = parser.add_subparsers(dest='command')

    # List Files and Folders
    subparsers.add_parser('list', help='List files and folders')

    # Create Folder
    parser_create_folder = subparsers.add_parser('create-folder', help='Create a new folder')
    parser_create_folder.add_argument('--name', required=True, help='Name of the new folder')

    # Upload File
    parser_upload = subparsers.add_parser('upload', help='Upload a file')
    parser_upload.add_argument('--path', required=True, help='Path of the file to upload')
    parser_upload.add_argument('--name', required=True, help='Name to save the uploaded file as on Google Drive')
    parser_upload.add_argument('--folder_id', help='ID of the folder to upload into (optional)')

    # Download File
    parser_download = subparsers.add_parser('download', help='Download a file')
    parser_download.add_argument('--file_id', required=True, help='ID of the file to download')
    parser_download.add_argument('--name', required=True, help='Name to save the downloaded file as')

    # Delete File or Folder
    parser_delete = subparsers.add_parser('delete', help='Delete a file or folder')
    parser_delete.add_argument('--file_id', required=True, help='ID of the file or folder to delete')

    # Rename File or Folder
    parser_rename = subparsers.add_parser('rename', help='Rename a file or folder')
    parser_rename.add_argument('--file_id', required=True, help='ID of the file or folder to rename')
    parser_rename.add_argument('--new_name', required=True, help='New name for the file or folder')

    # Check drive free space
    parser_drive_usage = subparsers.add_parser('drive-usage', help='Check drive free space')

    args = parser.parse_args()
    main(args)
