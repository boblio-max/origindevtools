import os
import subprocess
import zipfile

try:
    import tomllib  # Python 3.11+ standard library
except ImportError:
    import tomli as tomllib

# Define file paths
target_dir = r"C:\My Projects"
zip_path = os.path.join(target_dir, "Calculus-origin-lib.zip")

# Ensure the target directory exists
os.makedirs(target_dir, exist_ok=True)

# FIX: Use the explicit GitHub ZIP archive link, not the repository home page
download_url = "https://github.com/boblio-max/Calculus-origin-lib/archive/refs/heads/main.zip"

print(f"Downloading repository to {zip_path}...")
powershell_cmd = (
    f'Invoke-WebRequest -Uri "{download_url}" -OutFile "{zip_path}" '
    f'-UseBasicParsing -ErrorAction Stop'
)

# Call PowerShell to execute the download
result = subprocess.run(["powershell.exe", "-Command", powershell_cmd], capture_output=True, text=True)

if result.returncode != 0:
    print("Error executing PowerShell command:")
    print(result.stderr)
    exit(1)

print("Download complete!")

# Extract the valid ZIP file
print("Extracting ZIP archive...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(target_dir)
print(f"Extracted all files to {target_dir}")

# Search and read manifest.toml
manifest_path = None
for root, dirs, files in os.walk(target_dir):
    if "manifest.toml" in files:
        manifest_path = os.path.join(root, "manifest.toml")
        break

if manifest_path and os.path.exists(manifest_path):
    print(f"\nFound manifest file at: {manifest_path}")
    print("--- Content of manifest.toml ---")
    
    with open(manifest_path, "rb") as f:
        toml_data = tomllib.load(f)
        
    import pprint
    pprint.pprint(toml_data)
else:
    print("\nCould not find 'manifest.toml' anywhere inside the extracted files.")
