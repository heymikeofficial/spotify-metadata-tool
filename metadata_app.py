import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re

# ✅ Configure the page
st.set_page_config(page_title="Spotify Metadata Tool")
st.title("🎧 Spotify Metadata Extractor")

# ✅ Your real Spotify Developer credentials
import os

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


# ✅ Set up Spotipy with Client Credentials flow
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# 🔍 Extract the item type and Spotify ID from a track or album URL
def extract_id(url):
    pattern = r'spotify\.com/(track|album)/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

# 🎧 Display track metadata
def display_track(track):
    st.subheader("🎵 Track Info")
    st.write(f"**Title:** {track['name']}")
    st.write(f"**Artist(s):** {', '.join([artist['name'] for artist in track['artists']])}")
    st.write(f"**Album:** {track['album']['name']}")
    st.write(f"**Release Date:** {track['album']['release_date']}")
    st.write(f"**Label:** {track['album'].get('label', 'Not available')}")
    st.write(f"**ISRC:** {track['external_ids'].get('isrc', 'Not available')}")
    st.write(f"**Explicit:** {'Yes' if track['explicit'] else 'No'}")
    st.write(f"**Duration:** {int(track['duration_ms'] // 60000)}:{int((track['duration_ms'] % 60000) / 1000):02d}")

    # Album artwork
    st.image(track['album']['images'][0]['url'], width=250)

    # Spotify share link
    st.markdown(f"[🔗 Open in Spotify]({track['external_urls']['spotify']})", unsafe_allow_html=True)

# 📀 Display album metadata and tracklist
def display_album(album):
    st.subheader("💿 Album Info")
    st.write(f"**Title:** {album['name']}")
    st.write(f"**Artist(s):** {', '.join([artist['name'] for artist in album['artists']])}")
    st.write(f"**Release Date:** {album['release_date']}")
    st.write(f"**Label:** {album.get('label', 'Not available')}")
    st.write(f"**Total Tracks:** {album['total_tracks']}")

    # Album artwork
    st.image(album['images'][0]['url'], width=250)

    # Spotify share link
    st.markdown(f"[🔗 Open in Spotify]({album['external_urls']['spotify']})", unsafe_allow_html=True)

    # Track list with ISRCs
    st.subheader("📜 Track List + ISRCs")
    for track in album['tracks']['items']:
        try:
            track_data = sp.track(track['id'])
            isrc = track_data['external_ids'].get('isrc', 'Not available')
            st.write(f"- **{track['name']}** | ISRC: `{isrc}`")
        except Exception as e:
            st.write(f"- **{track['name']}** | ⚠️ Error retrieving ISRC: {e}")

# 🚀 App logic
spotify_url = st.text_input("Paste a Spotify track or album URL:")

if spotify_url:
    item_type, item_id = extract_id(spotify_url)
    if not item_id:
        st.error("❌ Invalid Spotify URL. Please paste a valid track or album link.")
    else:
        try:
            if item_type == "track":
                display_track(sp.track(item_id))
            elif item_type == "album":
                display_album(sp.album(item_id))
        except Exception as e:
            st.error(f"An error occurred: {e}")
