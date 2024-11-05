'''
Nick DeMaestri
11/4/2024
CS-391

Youtube Summarizer
Note: Written using the provided Lecture8 files provided (https://github.com/gnolankettering/lecture8/tree/main/youtube) as well as ChatGPT-4o with canvas.
'''

from flask import Flask, request, jsonify, render_template
from youtube_transcript_api import YouTubeTranscriptApi
from openai import OpenAI
import config

app = Flask(__name__)
client = OpenAI(api_key=config.OPENAI_API_KEY) #PUT YOUR API KEY AT config.py----------------------------------------------

def get_video_id(url):
    #Extract video ID from a YouTube URL.
    import re
    video_id = re.search(r'(?<=v=)[^&#]+', url)
    if not video_id:
        video_id = re.search(r'(?<=be/)[^&#]+', url)
    return video_id.group() if video_id else None

def fetch_transcript(video_id):
    #Fetches the transcript for the YouTube video.
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_generated_transcript(['en']).fetch()
    concatenated_text = " ".join(item['text'] for item in transcript)
    return concatenated_text

def summarize_text(text):
    #Summarize text using OpenAI API.
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Summarize the following text."},
            {"role": "assistant", "content": "Yes."},
            {"role": "user", "content": text}
        ]
    )
    return response.choices[0].message.content

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    url = request.json.get('url')
    video_id = get_video_id(url)
    
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    try:
        transcript = fetch_transcript(video_id)
        summary = summarize_text(transcript)
        return jsonify({'summary': summary})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
