import requests
import urllib.parse
import base64
import json
import re

# Spotify API credentials - replace these with your own
CLIENT_ID = 'Y89eea0ca7d574559884108d42755dd89'
CLIENT_SECRET = 'Y80050b1fa3fb4b1e8e2cbe52bf3946b7'

def get_access_token():
    """Get access token using client credentials flow"""
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {auth_base64}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    
    response = requests.post(url, headers=headers, data=data)

    # Print out what's going wrong if it fails
    if response.status_code != 200:
        print("❌ Failed to get access token.")
        print("Status Code:", response.status_code)
        print("Response:", response.text)
        return None

    return response.json().get("access_token")


def extract_id(url):
    """Extract Spotify ID from URL"""
    # Handle both track and album URLs
    pattern = r'spotify\.com/(track|album)/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def get_metadata(access_token, item_type, item_id):
    """Fetch metadata from Spotify API"""
    headers = {"Authorization": f"Bearer {access_token}"}
    
    if item_type == "track":
        url = f"https://api.spotify.com/v1/tracks/{item_id}"
    else:  # album
        url = f"https://api.spotify.com/v1/albums/{item_id}"
    
    response = requests.get(url, headers=headers)
    return response.json()

def print_metadata(metadata, item_type):
    """Print formatted metadata"""
    if item_type == "track":
        print("\nTrack Information:")
        print(f"Title: {metadata['name']}")
        print(f"Artist: {', '.join([artist['name'] for artist in metadata['artists']])}")
        print(f"Album: {metadata['album']['name']}")
        print(f"Release Date: {metadata['album']['release_date']}")
        print(f"Label: {metadata['album']['label'] if 'label' in metadata['album'] else 'Not available'}")
        print(f"ISRC: {metadata['external_ids']['isrc'] if 'external_ids' in metadata and 'isrc' in metadata['external_ids'] else 'Not available'}")
    else:  # album
        print("\nAlbum Information:")
        print(f"Title: {metadata['name']}")
        print(f"Artist: {', '.join([artist['name'] for artist in metadata['artists']])}")
        print(f"Release Date: {metadata['release_date']}")
        print(f"Label: {metadata['label'] if 'label' in metadata else 'Not available'}")
        print(f"Total Tracks: {metadata['total_tracks']}")

def main():
    # Get Spotify URL from user
    url = input("Enter Spotify track or album URL: ")
    
    # Extract ID and type
    item_type, item_id = extract_id(url)
    if not item_id:
        print("Invalid Spotify URL. Please provide a valid track or album URL.")
        return
    
    try:
        # Get access token
        access_token = get_access_token()
        if not access_token:
            print("No access token returned. Exiting.")
            return
        
        # Fetch metadata
        metadata = get_metadata(access_token, item_type, item_id)
        
        # Print metadata
        print_metadata(metadata, item_type)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main() 