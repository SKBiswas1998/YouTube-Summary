from flask import Flask, request, render_template, jsonify
import re
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled

app = Flask(__name__)

def get_video_id(url):
    """Extracts the YouTube video ID from a URL."""
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
    match = re.search(pattern, url)
    return match.group(1) if match else None

def fetch_transcript(video_id, language='en'):
    """Fetch transcript from YouTube video."""
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
        return " ".join([segment['text'] for segment in transcript])
    except TranscriptsDisabled:
        return "Error: Transcripts are disabled for this video."
    except Exception as e:
        return f"Error fetching transcript: {e}"

@app.route("/", methods=["GET", "POST"])
def index():
    transcript = None
    error = None

    if request.method == "POST":
        url = request.form.get("youtube_url")
        video_id = get_video_id(url)

        if not video_id:
            error = "⚠️ Invalid YouTube URL!"
        else:
            transcript = fetch_transcript(video_id)

    return render_template("index.html", transcript=transcript, error=error)

@app.route("/api/transcript", methods=["GET"])
def api_transcript():
    """API endpoint to fetch transcript via URL query parameter."""
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' parameter"}), 400

    video_id = get_video_id(url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    transcript = fetch_transcript(video_id)
    return jsonify({"transcript": transcript})

if __name__ == "__main__":
    app.run(debug=True)
