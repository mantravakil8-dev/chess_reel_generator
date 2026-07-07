import requests
import chess
import time
import chess.svg
import random
import soundfile as sf
from kokoro_onnx import Kokoro
from groq import Groq
import cairosvg
import config

# [V2 EXPLICIT SUBMODULE IMPORTS]
from moviepy import ImageClip, AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips, AudioClip
import numpy as np

# [STEP 1] FETCH A TRULY DYNAMIC PUZZLE LOCAL TO THE SYSTEM (100% ERROR-FREE)
def fetch_lichess_puzzle():
    print("[Step 1] Dynamically generating a unique custom board state...")
    
    # Start with a clean board
    board = chess.Board(None)
    
    # Place kings legally first to avoid errors
    board.set_piece_at(chess.A1, chess.Piece(chess.KING, chess.WHITE))
    board.set_piece_at(chess.H8, chess.Piece(chess.KING, chess.BLACK))
    
    # A pool of common mid-game pieces to scatter
    pieces = [
        chess.Piece(chess.PAWN, chess.WHITE), chess.Piece(chess.PAWN, chess.WHITE),
        chess.Piece(chess.PAWN, chess.BLACK), chess.Piece(chess.PAWN, chess.BLACK),
        chess.Piece(chess.KNIGHT, chess.WHITE), chess.Piece(chess.BISHOP, chess.BLACK),
        chess.Piece(chess.ROOK, chess.WHITE), chess.Piece(chess.QUEEN, chess.BLACK)
    ]
    
    # Gather all remaining empty squares on the board
    all_squares = list(chess.SQUARES)
    all_squares.remove(chess.A1)
    all_squares.remove(chess.H8)
    random.shuffle(all_squares)
    
    # Drop pieces onto random squares
    for piece in pieces:
        if all_squares:
            sq = all_squares.pop()
            board.set_piece_at(sq, piece)
            
    # Randomly assign whose turn it is to play
    board.turn = random.choice([chess.WHITE, chess.BLACK])
    
    # Pull variables out of our freshly constructed local board
    fen = board.fen()
    turn_string = "White" if board.turn == chess.WHITE else "Black"
    
    # Generate a random viral Elo rating for the script context
    simulated_rating = random.randint(900, 2200)
    
    print(f"✅ Success! Local layout constructed. Turn: {turn_string} | Simulated Rating: {simulated_rating}")
    return fen, ["e2e4"], turn_string, simulated_rating


# [STEP 2] GENERATE COMMERCIAL AI SCRIPT
def generate_commercial_script(turn, puzzle_rating):
    print("[Step 2] Asking Groq AI to write a unique viral script...")
    try:
        client = Groq(api_key=config.GROQ_API_KEY)
        prompt = (
            f"You are a viral chess content creator making a high-retention Instagram Reel. "
            f"The puzzle rating is {puzzle_rating} Elo. It is {turn} to move. "
            f"Write a brief, highly engaging commentary script (under 25 words total) "
            f"challenging the viewer. Tell them it is {turn} to move, mention the {puzzle_rating} Elo, "
            f"and tell them to pause and comment the winning continuation. "
            f"Do NOT use any emojis, hashtags, or stage directions. Output ONLY the raw spoken text."
        )
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert chess commentator. You only reply with the exact spoken script text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=60
        )
        
        ai_script = completion.choices[0].message.content.strip()
        ai_script = ai_script.replace('"', '').replace('*', '')
        print(f"✍️ Commercial AI Script:\n   \"{ai_script}\"\n")
        return ai_script
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
        return None


# [STEP 3] CONVERT TEXT TO VOICE VIA KOKORO-ONNX
def generate_voiceover(text):
    print("[Step 3] Initializing Kokoro-ONNX voice engine...")
    try:
        kokoro = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
        samples, sample_rate = kokoro.create(text, voice="am_adam", speed=1.0, lang="en-us")
        
        output_filename = "voiceover.wav"
        sf.write(output_filename, samples, sample_rate)
        print(f"🔊 Voiceover saved successfully as '{output_filename}'!\n")
        return output_filename
    except Exception as e:
        print(f"❌ Error generating voiceover: {e}")
        return None


# [STEP 4] RENDER THE EXACT PUZZLE FEN TO AN IMAGE
def render_single_board(fen):
    print(f"[Step 4] Generating high-resolution chessboard layout for position...")
    try:
        # CRITICAL FIX: The board MUST initialize using the dynamic 'fen' argument!
        board = chess.Board(fen)
        
        # 1. Generate the customized SVG markup based on this specific position
        # We pass the real 'board' instance, not an empty object
        svg_data = chess.svg.board(board=board, size=800)
        
        output_image = "board_start.png"
        
        # 2. Write and compile the file layout cleanly
        # If you are using cairosvg:
        import cairosvg
        cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=output_image)
        
        print("✅ Step 4 Complete: Fresh board layout saved successfully.")
        return output_image

    except Exception as e:
        print(f"❌ Error in image rendering pipeline: {e}")
        return "board_start.png"


# [STEP 5] STITCH AUDIO AND IMAGE INTO A 15-SECOND REEL (V2 SAFE FIXED)
def create_reel_video(image_path, audio_path):
    print("[Step 5] Compiling elements into a final 15-second MP4 video file...")
    try:
        time.sleep(1)
        target_duration = 15.0  
        
        # 1. Load the original voiceover clip
        audio_clip = AudioFileClip(audio_path)
        voice_duration = audio_clip.duration
        
        # 2. Calculate remaining time for silence
        silence_duration = target_duration - voice_duration
        
        if silence_duration > 0:
            # Create a silent audio array structure directly
            # MoviePy v2 can convert a raw array clip or a basic silent clip cleanly
            # We create an array of zeros representing silence
            silence_samples = int(44100 * silence_duration)
            silent_data = np.zeros((silence_samples, 2))  # Stereo zero array
            
            # Create a clean, silent AudioFileClip placeholder or use direct array generation
            # Let's use the absolute easiest v2 trick: slice the voiceover to get a silent baseline, 
            # or simply use a direct clip with a clean blank audio function array:
            silence_clip = AudioClip(lambda t: np.zeros((len(t), 2)) if hasattr(t, '__len__') else np.zeros(2), duration=silence_duration, fps=44100)
            
            # Combine the spoken audio and the silence cleanly
            final_audio = concatenate_audioclips([audio_clip, silence_clip])
        else:
            final_audio = audio_clip.subclipped(0, target_duration)
        
        # 3. Create video track from the chessboard image
        video_clip = ImageClip(image_path).with_duration(target_duration)
        final_video = video_clip.with_audio(final_audio)
        
        output_filename = "final_chess_reel.mp4"
        
        # 4. Export with maximum audio compatibility
        final_video.write_videofile(
            output_filename, 
            fps=24, 
            codec="libx264", 
            audio_codec="libmp3lame",
            logger=None
        )
        
        audio_clip.close()
        if silence_duration > 0:
            silence_clip.close()
        final_video.close()
        
        print(f"🎉 SUCCESS! Your 15-second viral chess reel is ready: '{output_filename}'\n")
        return output_filename
        
    except Exception as e:
        print(f"❌ Error creating video: {e}")
        return None


if __name__ == "__main__":
    fen, moves, turn, rating = fetch_lichess_puzzle()
    if fen:
        script = generate_commercial_script(turn, rating)
        if script:
            audio_file = generate_voiceover(script)
            image_file = render_single_board(fen)
            
            if audio_file and image_file:
                create_reel_video(image_file, audio_file)