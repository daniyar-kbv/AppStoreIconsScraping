import os
import shutil
from datetime import datetime

def merge_directories(source_dir1, source_dir2, destination_dir):
    # Create the destination directory if it doesn't exist
    os.makedirs(destination_dir, exist_ok=True)

    # Get the current date and time
    now = datetime.now()
    date_string = now.strftime("%d_%m_%Y")

    # Create the new directory name
    new_dir_name = f"icons_{date_string}"

    # Create the new directory inside the destination directory
    new_dir_path = os.path.join(destination_dir, new_dir_name)
    os.makedirs(new_dir_path, exist_ok=True)

    # Iterate through the files in the first source directory
    for filename in os.listdir(source_dir1):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # Copy the file to the new directory
            shutil.copy2(os.path.join(source_dir1, filename), new_dir_path)

    # Iterate through the files in the second source directory
    for filename in os.listdir(source_dir2):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            # Copy the file to the new directory
            shutil.copy2(os.path.join(source_dir2, filename), new_dir_path)

    print("Directories merged successfully!")

# Example usage
source_dir1 = "app_store_icons"
source_dir2 = "apple_icons"
destination_dir = "icons"
merge_directories(source_dir1, source_dir2, destination_dir)

