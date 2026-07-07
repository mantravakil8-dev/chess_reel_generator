import streamlit as st
import os
import time
import app  # This imports all your existing steps from app.py!
import qrcode
import io

# 1. Page Configuration
st.set_page_config(page_title="Chess Reel Generator", page_icon="♟️", layout="centered")

# 2. App Header
st.title("♟️ Automated Chess Reel Builder")
st.write("Generate high-retention 15-second chess shorts with AI voiceovers instantly.")

# 3. Sidebar QR Code Configuration
# Change this URL to match the exact Network URL shown in your terminal!
network_url = "http://192.168.1.52:8501" 

with st.sidebar:
    st.subheader("📱 Quick Mobile Access")
    st.write("Scan with your phone camera:")
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(network_url)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img_qr.save(buf, format="PNG")
    st.image(buf.getvalue(), width=200)

st.divider()

# 4. Main Control Panel Columns
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Control Panel")
    st.write("Click below to pull a random puzzle, write an AI script, and compile your video asset.")
    
    if st.button("🚀 Generate New Reel", type="primary", use_container_width=True):
        with st.status("🎬 Processing pipeline...", expanded=True) as status:
            
            st.write("🎲 Shuffling puzzle vault...")
            fen, moves, turn, rating = app.fetch_lichess_puzzle()
            st.toast(f"Loaded {rating} Elo Puzzle!", icon="✅")
            
            st.write("🧠 Querying Groq for viral script...")
            script = app.generate_commercial_script(turn, rating)
            st.text_area("Generated Script:", value=script, height=70, disabled=True)
            
            st.write("🔊 Generating AI voiceover & rendering board...")
            audio_file = app.generate_voiceover(script)
            image_file = app.render_single_board(fen)
            
            st.write("🎥 Compiling 15-second MP4 container...")
            video_file = app.create_reel_video(image_file, audio_file)
            
            status.update(label="🎉 Reel Compiled Successfully!", state="complete", expanded=False)
        
        # 5. Display Output with Safe Cache-Buster Fix
        if video_file and os.path.exists(video_file):
            with col2:
                st.subheader("Your Generated Reel")
                
                # Safe cache-buster: Read the raw image file bytes directly!
                # This guarantees Streamlit always renders the newest data.
                try:
                    with open(image_file, "rb") as img_f:
                        img_bytes = img_f.read()
                    st.image(img_bytes, caption=f"Starting Position ({rating} Elo)", use_container_width=True)
                except Exception as img_err:
                    st.error(f"Could not load preview frame: {img_err}")
                
                # The video player
                st.video(video_file)
                
                with open(video_file, "rb") as file:
                    st.download_button(
                        label="📥 Download Video",
                        data=file,
                        file_name="viral_chess_reel.mp4",
                        mime="video/mp4",
                        use_container_width=True
                    )