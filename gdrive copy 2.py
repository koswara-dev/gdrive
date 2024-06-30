import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/drive']

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)

service = build('drive', 'v3', credentials=credentials)

def get_drive_files(parent_id=None):
    query = "'root' in parents" if not parent_id else f"'{parent_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def local_to_drive(local_dir, parent_id=None):
    drive_files = {file['name']: file['id'] for file in get_drive_files(parent_id)}
    for filename in os.listdir(local_dir):
        filepath = os.path.join(local_dir, filename)
        if os.path.isfile(filepath) and filename not in drive_files:
            upload_file(filepath, parent_id)
            print(f"Uploaded: {filename}")

def drive_to_local(local_dir, parent_id=None):
    drive_files = get_drive_files(parent_id)
    local_files = set(os.listdir(local_dir))
    
    for file in drive_files:
        if file['name'] not in local_files:
            destination_path = os.path.join(local_dir, file['name'])
            download_file(file['id'], destination_path)
            print(f"Downloaded: {file['name']}")

def sync_files_and_folders():
    local_dir = input("Enter the local directory to sync: ")
    parent_id = input("Enter the Google Drive parent folder ID (optional): ") or None

    if not os.path.exists(local_dir):
        print(f"Local directory {local_dir} does not exist.")
        return

    local_to_drive(local_dir, parent_id)
    drive_to_local(local_dir, parent_id)
    print("Sync completed.")

def create_folder(folder_name, parent_id=None):
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        folder = service.files().create(body=file_metadata, fields='id').execute()
        print(f"Folder {folder_name} created with ID: {folder.get('id')}")
        return folder.get('id')
    except Exception as e:
        print(f"An error occurred while creating the folder: {e}")

def delete_file_or_folder(file_id):
    try:
        service.files().delete(fileId=file_id).execute()
        print(f"File or folder with ID: {file_id} has been deleted.")
    except Exception as e:
        print(f"An error occurred while deleting the file or folder: {e}")

def list_files_and_folders():
    results = service.files().list(
        pageSize=100,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files and Folders:')
        for item in items:
            print(f"{item['name']} ({item['id']}) - {item['mimeType']}")

def upload_file(file_path, parent_id=None):
    try:
        file_metadata = {'name': os.path.basename(file_path)}
        if parent_id:
            file_metadata['parents'] = [parent_id]
        media = MediaFileUpload(file_path, resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"File {file_path} uploaded with ID: {file.get('id')}")
        return file.get('id')
    except Exception as e:
        print(f"An error occurred while uploading the file: {e}")

def download_file(file_id, destination_path):
    try:
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(destination_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%")
    except Exception as e:
        print(f"An error occurred while downloading the file: {e}")

# Fungsi untuk memeriksa kapasitas drive yang tersedia
def check_drive_free_space():
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
    def invalid_choice():
        print("Invalid choice. Please select a valid operation.")

    operations = {
        1: lambda: create_folder(input("Enter folder name: "), input("Enter parent folder ID (optional): ") or None),
        2: sync_files_and_folders,
        3: lambda: delete_file_or_folder(input("Enter file or folder ID: ")),
        4: lambda: list_files_and_folders,
        5: lambda: upload_file(input("Enter file path to upload: "), input("Enter parent folder ID (optional): ") or None),
        6: lambda: download_file(input("Enter file ID: "), input("Enter destination path: ")),
        7: check_drive_free_space
    }

    while True:
        print("""
        Select an operation:
        0. Exit
        1. Create new folder
        2. Sync files and folders
        3. Delete file or folder
        4. Get list of folders
        5. Upload file
        6. Download file
        7. Check drive free space
        """)

        try:
            choice = int(input("Enter your choice: "))
            if choice == 0:
                print("Exiting...")
                break
            operations.get(choice, invalid_choice)()
        except ValueError:
            print("Please enter a valid number.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
