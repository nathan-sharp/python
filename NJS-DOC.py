import os
import random
import re
import csv
from datetime import datetime

def generate_unambiguous_id(prefix="DOC-", length=6):
    """Generates a random ID excluding ambiguous characters (0, O, 1, I)."""
    safe_chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    random_str = ''.join(random.choices(safe_chars, k=length))
    return f"{prefix}{random_str}"

def get_existing_ids(directory_path, prefix="DOC-"):
    """Scans the directory for existing IDs matching the DOC-XXXXXX pattern."""
    existing_ids = set()
    pattern = re.compile(rf"{prefix}([A-Z0-9]{{{6}}})", re.IGNORECASE)
    
    if not os.path.exists(directory_path):
        # We don't print a warning here anymore since it's normal to start empty
        return existing_ids

    for filename in os.listdir(directory_path):
        match = pattern.search(filename)
        if match:
            existing_ids.add(match.group(0).upper())
            
    return existing_ids

def create_unique_document_id(directory_path):
    """Generates a new safe ID and ensures it doesn't already exist."""
    existing_ids = get_existing_ids(directory_path)
    
    while True:
        new_id = generate_unambiguous_id()
        if new_id not in existing_ids:
            return new_id

def log_to_tracker(doc_id, title, tracker_file):
    """Logs the new ID, title, and creation date to a CSV file."""
    # Check if the file already exists so we know whether to write headers
    file_exists = os.path.isfile(tracker_file)
    
    # Open the CSV file in 'append' mode ('a')
    with open(tracker_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # If it's a brand new tracker, write the column headers first
        if not file_exists:
            writer.writerow(['Document ID', 'Title', 'Date Created'])
            
        # Write the document data
        date_created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        writer.writerow([doc_id, title, date_created])

# --- Configuration & Execution ---
if __name__ == "__main__":
    # ⚠️ REPLACE this path with your actual documents folder path
    DOCUMENTS_FOLDER = r"C:\Users\User\Documents" 
    
    # The tracker will be saved in the same folder as your documents
    TRACKER_FILE = os.path.join(DOCUMENTS_FOLDER, "Master_Document_Register.csv")
    
    # 1. Ask the user for the document title
    print("--- New Document ID Generator ---")
    doc_title = input("Enter the title/description of the new document: ").strip()
    
    # Prevent empty titles
    if not doc_title:
        print("Error: Document title cannot be empty. Please run the script again.")
    else:
        try:
            # 2. Generate the ID
            new_document_id = create_unique_document_id(DOCUMENTS_FOLDER)
            
            # 3. Log it to the CSV
            log_to_tracker(new_document_id, doc_title, TRACKER_FILE)
            
            # 4. Success Output
            print("\n✅ Success!")
            print(f"Generated ID: {new_document_id}")
            print(f"Title:        {doc_title}")
            print(f"Tracker updated: {TRACKER_FILE}")
            
        except Exception as e:
            print(f"\n❌ An error occurred: {e}")
