"""
Setup script to download and install TinyMCE for the LearnOnline project.

This script automatically downloads the TinyMCE library from the official CDN
and sets it up in the correct directory for local hosting.
"""

import urllib.request
import zipfile
from pathlib import Path

# Configuration
TINYMCE_VERSION = "6.8.5"
TINYMCE_DOWNLOAD_URL = f"https://download.tiny.cloud/tinymce/community/tinymce_{TINYMCE_VERSION}.zip"
PROJECT_ROOT = Path(__file__).parent
TINYMCE_DIR = PROJECT_ROOT / "static" / "courses"
TINYMCE_ZIP_PATH = TINYMCE_DIR / "tinymce.zip"


def setup_tinymce():
    """Download and setup TinyMCE for local hosting."""
    print("Setting up TinyMCE for LearnOnline project...")
    print(f"Using TinyMCE v{TINYMCE_VERSION} (community version without API key requirement)")
    
    # Create TinyMCE directory if it doesn't exist
    TINYMCE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {TINYMCE_DIR}")
    
    # Download TinyMCE
    print(f"Downloading TinyMCE v{TINYMCE_VERSION} from {TINYMCE_DOWNLOAD_URL}...")
    try:
        urllib.request.urlretrieve(TINYMCE_DOWNLOAD_URL, TINYMCE_ZIP_PATH)
        print(f"Downloaded TinyMCE to {TINYMCE_ZIP_PATH}")
    except Exception as e:
        print(f"Error downloading TinyMCE: {e}")
        return False
    
    # Extract TinyMCE
    print("Extracting TinyMCE...")
    try:
        with zipfile.ZipFile(TINYMCE_ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(TINYMCE_DIR)
        print("Extracted TinyMCE successfully")
    except Exception as e:
        print(f"Error extracting TinyMCE: {e}")
        return False
    
    # Clean up zip file
    try:
        TINYMCE_ZIP_PATH.unlink()
        print("Cleaned up temporary files")
    except Exception as e:
        print(f"Warning: Could not remove temporary file: {e}")
    
    print("\nTinyMCE setup completed successfully!")
    print("You can now use the self-hosted TinyMCE editor in the LearnOnline project.")
    print("This is the community version which does not require an API key.")
    return True


if __name__ == "__main__":
    success = setup_tinymce()
    if not success:
        exit(1)