from flask import Flask, render_template,request
import glob
import os
import sys
from youtube_search import YoutubeSearch
from pydub import AudioSegment
import youtube_dl
import moviepy.editor as mp
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pydub import AudioSegment
import moviepy.editor as mp
import zipfile

app=Flask(__name__)
@app.route('/')
def index():
    return render_template('index.html')

@app.route("/",methods=['POST'])
def home():
    channel_name=request.form['singername']
    no_of_videos=request.form['no_of_videos']
    trim_time=request.form['timestamp']
    email=request.form['email']
    main(channel_name,no_of_videos,trim_time,email)
    return "<h1><center>Thank You.</center></h1>"

def download_audios(url, n):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl: 
        ydl.download([url])

def cut_audios(singer_name, n, duration):
    for i in range(n):
        audio = AudioSegment.from_file(singer_name)
        audio = audio[:duration * 1000]
        audio.export('audio'+str(i)+'.mp3', format='mp3')

def merge_audios(singer_name, n, output_file):
    combined = AudioSegment.from_mono_audiosegments(
        [AudioSegment.from_file('audio'+str(i)+'.mp3') for i in range(n)]
    )
    combined.export(output_file, format='mp3')

def main(singer_name,n,duration,email):
    n = int(n)    
    duration = int(duration)
    results = YoutubeSearch(singer_name, max_results=n).to_dict()
    links=[]
    for i in range(n):
        links.append(results[i]['url_suffix'])
        links[i]="https://www.youtube.com/"+links[i]
        download_audios(links[i], n)
    all_mp3s = glob.glob('./*.mp3')
    for i in range(n):
        audio_file = all_mp3s[i]
        cut_audios(audio_file, n, duration)
    for i in range(len(all_mp3s)):
        os.remove(all_mp3s[i])
    audio_folder='.'
    audio_files = [audio_folder+'/'+img for img in os.listdir(audio_folder) if img.endswith(".mp3")]
    print(audio_files)
    audios = []
    for audio in audio_files :
        audios.append(mp.AudioFileClip(audio))
    audioClips = mp.concatenate_audioclips([audio for audio in audios])
    audioClips.write_audiofile("./final.mp3")
    zip = zipfile.ZipFile("102003650.zip", "w", zipfile.ZIP_DEFLATED)
    zip.write("./final.mp3")
    zip.close()
    fromaddr = "jchopra_be20@thapar.edu"
    toaddr = email
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Mashup Assignment"
    filename = "102003650.zip"
    attachment = open("./102003650.zip", "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(fromaddr, "JigishaChopra@27")
    text = msg.as_string()
    s.sendmail(fromaddr, toaddr, text)
    s.quit()
    
if __name__=="__main__":
    app.run(debug=True)