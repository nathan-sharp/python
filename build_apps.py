import os
import shutil
import subprocess
import sys

def build_apps():
    # --- Configuration ---
    source_folder = "TkInter"
    output_folder = "applications"
    temp_folder = "temp_build_artifacts" 
    
    # Define where icons live (Source) and where they should go (Output)
    icons_source = os.path.join(source_folder, "icons")
    icons_dest = os.path.join(output_folder, "icons")

    # Check for PyInstaller
    if shutil.which("pyinstaller") is None:
        print("Error: PyInstaller is not found. Please run: pip install pyinstaller")
        return

    if not os.path.exists(source_folder):
        print(f"Error: I cannot find the folder '{source_folder}'.")
        return

    # Create output folder
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    # Find Python files
    files = [f for f in os.listdir(source_folder) if f.endswith('.py')]
    
    if not files:
        print("No Python files found to build.")
        return

    print(f"Found {len(files)} apps to build: {', '.join(files)}\n")

    # --- Build Process ---
    for filename in files:
        print(f"--- Building {filename} ---")
        script_path = os.path.join(source_folder, filename)
        
        command = [
            "pyinstaller",
            "--noconsole",
            "--onefile",
            f"--distpath={output_folder}",
            f"--workpath={temp_folder}",
            f"--specpath={temp_folder}",
            script_path
        ]

        try:
            subprocess.run(command, check=True)
            print(f"Successfully built: {filename}")
        except subprocess.CalledProcessError:
            print(f"!!! Failed to build: {filename}")

    # --- Copy Icons Folder ---
    # This ensures the icons are sitting right next to the new .exe files
    if os.path.exists(icons_source):
        print(f"\n--- Copying Icon Pack ---")
        try:
            # dirs_exist_ok=True allows it to overwrite if we build multiple times
            shutil.copytree(icons_source, icons_dest, dirs_exist_ok=True)
            print(f"Copied 'icons' folder to '{output_folder}/icons'")
        except Exception as e:
            print(f"Warning: Could not copy icons folder: {e}")
    else:
        print("\nNotice: No 'icons' folder found in TkInter/. Apps will use fallback pixel art.")

    # --- Cleanup ---
    print("\n--- Cleaning up temporary files ---")
    if os.path.exists(temp_folder):
        try:
            shutil.rmtree(temp_folder)
            print("Deleted temporary build artifacts.")
        except Exception as e:
            print(f"Could not delete temp folder: {e}")

    pycache = os.path.join(source_folder, "__pycache__")
    if os.path.exists(pycache):
        shutil.rmtree(pycache)
        print("Deleted __pycache__")

    print(f"\nAll done! You can now zip the '{output_folder}' folder to share your apps.")

if __name__ == "__main__":
    build_apps()