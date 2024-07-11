from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip
from TextSummarizer.pipeline.prediction import PredictionPipeline
app = Flask(__name__)

# Configure Speech Recognizer
recognizer = sr.Recognizer()

@app.route('/transcribe-summarize', methods=['POST'])
def transcribe_summarize():
    try:
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']

        if file.filename == '':
            return "No selected file"

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join('uploads', filename)
            
            # Ensure the uploads directory exists
            if not os.path.exists('uploads'):
                os.makedirs('uploads')

            file.save(file_path)

            # Extract audio from the uploaded video file
            video = VideoFileClip(file_path)
            audio_path = os.path.join('uploads', f"{filename.rsplit('.', 1)[0]}.wav")
            video.audio.write_audiofile(audio_path)

            # Use Google Speech Recognition to transcribe the audio
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)

            transcribed_text = recognizer.recognize_google(audio_data)

            # Perform text summarization
            obj = PredictionPipeline()
            summarized_text = obj.predict(transcribed_text)

            # Render the result template with the transcribed and summarized text
            return render_template('result.html', transcribed_text=transcribed_text, summarized_text=summarized_text)
    except FileNotFoundError:
        return "File not found"
    except Exception as e:
        return str(e)

@app.route('/transcribe-summarize/MOM', methods=['GET', 'POST'])
def render_mom_form():
    try:
        if request.method == 'POST':
            # Retrieve form data
            firstname = request.form['firstname']
            organizer = request.form['organizer']
            topic = request.form['topic']
            date = request.form['date']
            attendees = request.form['attendees']
            subject = request.form['subject']

            # Render the HTML template with form data
            return render_template('MinutesOfMeeting.html', firstname=firstname, organizer=organizer, topic=topic, date=date, attendees=attendees, subject=subject)
        else:
            # Retrieve the summarized text from the request arguments
            summarized_text = request.args.get('summarized_text', '')
            # Render the HTML template with the summarized text
            return render_template('MinutesOfMeeting.html', summarized_text=summarized_text)
    except Exception as e:
        return str(e)

@app.route('/transcribe-summarize/MOM/download-mom', methods=['GET', 'POST'])
def download_mom():
    try:
        # Retrieve form data
        firstname = request.form['firstname']
        organizer = request.form['organizer']
        topic = request.form['topic']
        date = request.form['date']
        attendees = request.form['attendees']
        subject = request.form['subject']

        # Render the DownloadMom.html template with form data
        return render_template('DownloadMom.html', firstname=firstname, organizer=organizer, topic=topic, date=date, attendees=attendees, subject=subject)
    except Exception as e:
        return str(e)

@app.route("/summarize", methods=["POST"])
def summarize():
    try:
        text = request.form.get("text")
        if not text:
            return "Please enter some text to summarize."
        
        obj = PredictionPipeline()
        summarized_text = obj.predict(text)
        
        return render_template("result.html", transcribed_text=text, summarized_text=summarized_text)
    except Exception as e:
        return str(e)

@app.route('/')
def index():
    image_url = 'static/images/Cyber-Security.png'
    return render_template('index.html', image_url=image_url)

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(host="0.0.0.0", port=8080, debug=True)
