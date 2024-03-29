import yt_dlp as youtube_dl
import pandas as pd
import os
import wave
import math
import whisper

WAV_FILES_DIR = "wav_files"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
AUDIO_CHUNKS_DIR = "audio-chunks"
AUDIO_LIMIT=60

def count_files(directory):
    if not os.path.isdir(directory):
        raise ValueError("The provided path is not a directory.")

    file_count = 0
    for _, _, files in os.walk(directory):
        file_count += len(files)

    return file_count

def get_wav_duration(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        # Get the number of frames and the frame rate (sample rate) of the audio
        num_frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()

        # Calculate the duration of the audio in seconds
        duration = num_frames / frame_rate

    return duration

def split_wav(input_file, audio_files_dir, chunk_duration=30):

    with wave.open(input_file, 'rb') as wav_file:
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        num_channels = wav_file.getnchannels()
        num_frames = wav_file.getnframes()

        chunk_size = chunk_duration * frame_rate
        num_chunks = math.ceil(num_frames / chunk_size)

        for i in range(num_chunks):
            output_file = f"{audio_files_dir}/chunk_{i}.wav"
            if not os.path.exists(output_file):
                with wave.open(output_file, 'wb') as output_wav:
                    output_wav.setparams((num_channels, sample_width, frame_rate, 0, 'NONE', 'not compressed'))
                    start_frame = i * chunk_size
                    end_frame = min((i + 1) * chunk_size, num_frames)
                    wav_file.setpos(start_frame)
                    output_wav.writeframes(wav_file.readframes(end_frame - start_frame))




def is_file_in_directory(directory, filename):
    files_in_directory = os.listdir(directory)
    return filename in files_in_directory


def extract_audio(video_url, output_file):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'outtmpl': output_file,
        'quiet': False
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])

def transcribe_large_audio(path,video_id):
    """Split audio into chunks and apply speech recognition"""
    
    # sound = AudioSegment.from_wav(path)

    
    # Split audio where silence is 700ms or greater and get chunks
    # chunks = split_on_silence(sound, min_silence_len=700, silence_thresh=sound.dBFS-14, keep_silence=700)

    audio_files_dir = f"{AUDIO_CHUNKS_DIR}/{video_id}"
    if not os.path.isdir(audio_files_dir):
        os.mkdir(audio_files_dir)

    split_wav(path, audio_files_dir, 30)
    
    whole_text = ""

    model = whisper.load_model("base")
    
    for i in range(count_files(audio_files_dir)):
       
        chunk_filename = os.path.join(audio_files_dir, f"chunk_{i}.wav")
        # audio_chunk.export(chunk_filename, format="wav")
        
        text = model.transcribe(chunk_filename)
        print(text)
        whole_text += text['text'] + "\n"
    
    return whole_text

def audio_to_text(audio_file, video_id):
    duration = get_wav_duration(audio_file)

    text = ""

    if duration < AUDIO_LIMIT:
        model = whisper.load_model("base")
        text = model.transcribe(audio_file)
    else:
        text = transcribe_large_audio(audio_file,video_id)

    return text


def fetch_transcript(url,video_id):

    if not os.path.isdir(WAV_FILES_DIR):
        os.mkdir(WAV_FILES_DIR)

    audio_file = f"{WAV_FILES_DIR}/{video_id}"
    if not is_file_in_directory(WAV_FILES_DIR, f"{video_id}.wav"):
        extract_audio(url, audio_file)
    
    audio_file_path = f"{audio_file}.wav"
    transcript = audio_to_text(audio_file_path, video_id)
    return transcript
    
