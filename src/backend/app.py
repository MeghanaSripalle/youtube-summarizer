from flask import Flask, Response, jsonify,request
from youtube_transcript_api import YouTubeTranscriptApi
import json
from transformers import T5Tokenizer, T5ForConditionalGeneration
from flask_cors import CORS
from utils import fetch_transcript


app = Flask(__name__)
CORS(app)
    
@app.route('/api/summarize', methods=['GET'])
def get_summarized_transcript():
    
    youtube_url = request.args.get('youtube_url')
    video_id = youtube_url.split('v=')[-1].split('&')[0]
    
    transcript = fetch_transcript(youtube_url,video_id)

    if len(transcript.split(" ")) > 1024:
        return "Transcript too long",500
    
    summary = get_summary(transcript)
    
    return jsonify(summary), 200

def get_youtube_transcript(video_id):
    transcript_raw = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
    transcript = []
    for segment in transcript_raw:
        if segment["text"] != "[Music]":
            transcript.append(segment["text"])
    
    final_transcript = " ".join(transcript)
    if len(final_transcript.split(" ")) > 1024:
        return None
    return final_transcript

def get_summary(transcript):
    tokenizer = T5Tokenizer.from_pretrained("t5-base")
    model = T5ForConditionalGeneration.from_pretrained("t5-base")

    input_text = "summarize: " + transcript
    input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(input_ids, max_length=150, num_beams=4, length_penalty=2.0, early_stopping=True)

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summary


if __name__ == '__main__':
    app.run(debug=True)