# Google Drive File Management Script

This script allows you to manage files and folders on Google Drive using Google Drive API. It supports listing, uploading, downloading, deleting, and renaming files or folders, as well as checking the remaining free space on your drive.

## Prerequisites

Before using this script, ensure you have:

1. **Python 3.x** installed.
2. A **Google Cloud Project** with the **Google Drive API** enabled.
3. **Service Account Credentials** JSON file from Google Cloud.
4. A `.env` file with the path to your Service Account Credentials JSON file.

## Setup

1. **Clone the repository:**
    ```bash
    git clone https://github.com/koswara-dev/gdrive
    cd gdrive
    ```

2. **Install required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Create a `.env` file:**  
    Create a file named `.env` in the root directory and add the following line:
    ```plaintext
    SERVICE_ACCOUNT_FILE=path/to/your/service_account.json
    ```
   
## Usage

Run the script with the appropriate command to perform different operations:

### List Files and Folders

To list files and folders in your Google Drive:
```bash
python gdrive.py list
```

### Create a New Folder

To create a new folder:
```bash
python gdrive.py create-folder --name "New Folder Name"
```

### Upload a File

To upload a file:
```bash
python gdrive.py upload --path "/local/path/to/file.txt" --name "file_on_drive.txt" --folder_id "optional_folder_id"
```

### Download a File

To download a file:
```bash
python gdrive.py download --file_id "file_id_on_drive" --name "save_as_name.txt"
```

### Delete a File or Folder

To delete a file or folder:
```bash
python gdrive.py delete --file_id "file_or_folder_id"
```

### Rename a File or Folder

To rename a file or folder:
```bash
python gdrive.py rename --file_id "file_or_folder_id" --new_name "New Name"
```

### Check Drive Free Space

To check the available free space in your Google Drive:
```bash
python gdrive.py drive-usage
```

## Example Commands

- **List files and folders:**
    ```bash
    python gdrive.py list
    ```

- **Create a folder named "Projects":**
    ```bash
    python gdrive.py create-folder --name "Projects"
    ```

- **Upload a file `document.txt` to a folder with ID `1n2y3z`:**
    ```bash
    python gdrive.py upload --path "./document.txt" --name "uploaded_document.txt" --folder_id "1n2y3z"
    ```

- **Download a file with ID `1GhJkL` and save it as `downloaded_file.txt`:**
    ```bash
    python gdrive.py download --file_id "1GhJkL" --name "downloaded_file.txt"
    ```

- **Delete a file with ID `1GhJkL`:**
    ```bash
    python gdrive.py delete --file_id "1GhJkL"
    ```

- **Rename a file with ID `1GhJkL` to `new_name.txt`:**
    ```bash
    python gdrive.py rename --file_id "1GhJkL" --new_name "new_name.txt"
    ```

- **Check drive free space:**
    ```bash
    python gdrive.py drive-usage
    ```

## Buy me a coffe

Jika Anda menyukai proyek ini dan ingin mendukung pengembangannya lebih lanjut, pertimbangkan untuk membeli kami kopi!

[![Buy Me a Coffee](https://www.buymeacoffee.com/assets/img/guidelines/download-assets-sm-1.svg)](https://www.buymeacoffee.com/kudajengke404)
