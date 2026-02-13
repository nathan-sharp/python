import os
import shutil
import subprocess
import sys

def build_apps():
    # --- Configuration ---
    source_folder = "TkInter"
    output_folder = "applications"
    temp_folder = "temp_build_artifacts" # We'll dump all temp files here to delete them easily later

    # Check if PyInstaller is installed
    if shutil.which("pyinstaller") is None:
        print("Error: PyInstaller is not found. Please run: pip install pyinstaller")
        return

    # Ensure source folder exists
    if not os.path.exists(source_folder):
        print(f"Error: I cannot find the folder '{source_folder}'. Make sure this script is next to it.")
        return

    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    # Find all Python files in the source folder
    files = [f for f in os.listdir(source_folder) if f.endswith('.py')]
    
    if not files:
        print("No Python files found to build.")
        return

    print(f"Found {len(files)} apps to build: {', '.join(files)}\n")

    # --- Build Process ---
    for filename in files:
        print(f"--- Building {filename} ---")
        script_path = os.path.join(source_folder, filename)
        
        # This is the command that runs in the terminal
        command = [
            "pyinstaller",
            "--noconsole",                  # Don't show the black terminal window
            "--onefile",                    # Bundle everything into a single .exe/.app
            f"--distpath={output_folder}",  # Put the final app in 'applications'
            f"--workpath={temp_folder}",    # Put temp build files in a specific folder
            f"--specpath={temp_folder}",    # Put the .spec config file in that same temp folder
            script_path
        ]

        try:
            # Run the command and wait for it to finish
            subprocess.run(command, check=True)
            print(f"Successfully built: {filename}")
        except subprocess.CalledProcessError:
            print(f"!!! Failed to build: {filename}")

    # --- Cleanup ---
    print("\n--- Cleaning up temporary files ---")
    if os.path.exists(temp_folder):
        try:
            shutil.rmtree(temp_folder)
            print(f"Deleted temporary folder: {temp_folder}")
        except Exception as e:
            print(f"Could not delete temp folder: {e}")

    # Optional: Delete __pycache__ inside the source folder if it exists
    pycache = os.path.join(source_folder, "__pycache__")
    if os.path.exists(pycache):
        shutil.rmtree(pycache)
        print("Deleted __pycache__")

    print(f"\nAll done! Your apps are waiting in the '{output_folder}' folder.")

if __name__ == "__main__":
    build_apps()
