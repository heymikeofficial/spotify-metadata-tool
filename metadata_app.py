import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
import os
from fpdf import FPDF
import tempfile

# Spotify Credentials (pulled from Streamlit Secrets)
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# Utility functions
def extract_id(url):
    pattern = r'spotify\.com/(track|album)/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1), match.group(2)
    return None, None

def format_duration(ms):
    minutes = ms // 60000
    seconds = (ms % 60000) // 1000
    return f"{minutes}:{str(seconds).zfill(2)}"

# 🧾 PDF Generator
def generate_album_pdf(album, tracklist):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, album['name'], ln=True, align="C")

    pdf.set_font("Arial", '', 12)
    pdf.ln(5)
    pdf.cell(200, 10, f"Artist(s): {', '.join([artist['name'] for artist in album['artists']])}", ln=True)
    pdf.cell(200, 10, f"Release Date: {album['release_date']}", ln=True)
    pdf.cell(200, 10, f"Label: {album.get('label', 'Not available')}", ln=True)
    pdf.cell(200, 10, f"Total Tracks: {album['total_tracks']}", ln=True)
    pdf.cell(200, 10, f"Spotify: {album['external_urls']['spotify']}", ln=True)

    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "Track Title", 1)
    pdf.cell(60, 10, "ISRC", 1)
    pdf.cell(30, 10, "Duration", 1)
    pdf.ln()

    pdf.set_font("Arial", '', 12)
    for track in tracklist:
        pdf.cell(90, 10, track['name'][:30], 1)
        pdf.cell(60, 10, track['isrc'], 1)
        pdf.cell(30, 10, track['duration'], 1)
        pdf.ln()

    # Save to temp location
    temp_dir = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_dir.name)
    return temp_dir.name

# Streamlit layout
st.set_page_config(page_title="Spotify Metadata Tool")
st.title("Spotify Metadata Tool 🎧")
url = st.text_input("Paste a Spotify **album** URL:")

if url:
    item_type, item_id = extract_id(url)

    if item_type != "album":
        st.warning("This feature only works with album links right now.")
    else:
        try:
            album = sp.album(item_id)
            st.subheader("💿 Album Metadata")
            st.write(f"**Title:** {album['name']}")
            st.write(f"**Artist(s):** {', '.join([artist['name'] for artist in album['artists']])}")
            st.write(f"**Release Date:** {album['release_date']}")
            st.write(f"**Label:** {album.get('label', 'Not available')}")
            st.write(f"**Total Tracks:** {album['total_tracks']}")
            st.image(album['images'][0]['url'], width=250)
            st.markdown(f"[Open in Spotify]({album['external_urls']['spotify']})")

            st.subheader("📜 Track List")
            tracklist = []
            for track in album['tracks']['items']:
                track_data = sp.track(track['id'])
                tracklist.append({
                    "name": track_data['name'],
                    "isrc": track_data['external_ids'].get('isrc', 'Not available'),
                    "duration": format_duration(track_data['duration_ms'])
                })
                st.write(f"- **{track_data['name']}** | ISRC: `{tracklist[-1]['isrc']}` | {tracklist[-1]['duration']}")

            # Generate PDF button
            if st.button("📄 Download Album Metadata One-Sheet (PDF)"):
                pdf_path = generate_album_pdf(album, tracklist)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Click to Download PDF",
                        data=f,
                        file_name=f"{album['name'].replace(' ', '_')}_metadata.pdf",
                        mime="application/pdf"
                    )
        except Exception as e:
            st.error(f"❌ Error fetching album data: {e}")
