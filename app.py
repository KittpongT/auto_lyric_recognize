import streamlit as st
import requests
import json
import os
from pytube import YouTube
import librosa, librosa.display
import soundfile as sf
from glob import glob
from scipy.io.wavfile import read, write
import io

os.system("apt install ffmpeg")

API_TOKEN = "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"
API_URL_ktp = "https://api-inference.huggingface.co/models/Kittipong/wav2vec2-th-vocal-domain"
API_URL_airesearch = "https://api-inference.huggingface.co/models/airesearch/wav2vec2-large-xlsr-53-th"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

st.title('Auto lyric recognizer🎤')

col1, col2 = st.columns(2)

def query(API_URL,data):
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))

def split_file(path):
    file_name = path
    audio, sr = librosa.load(file_name)

    buffer = 60 * sr
    samples_total = len(audio)
    samples_wrote = 0
    counter = 1

    while samples_wrote < samples_total:

        if buffer > (samples_total - samples_wrote):
            buffer = samples_total - samples_wrote

        block = audio[samples_wrote : (samples_wrote + buffer)]
        out_filename = "split_" + str(counter) + ".wav"

        sf.write(out_filename, block, sr)
        counter += 1
        samples_wrote += buffer

def audio_analysis(audio):
    with col2:
        if audio!=0:
            output1 = query(API_URL_ktp,audio)
            output2 = query(API_URL_airesearch,audio)
            
            with st.expander("ผลลัพท์จากโมเดล Kittipong/wav2vec2-th-vocal-domain"):
                st.write(f"{output1}")
            with st.expander("ผลลัพท์จากโมเดล airesearch/wav2vec2-large-xlsr-53-th"):
                st.write(f"{output2}")
        else:

            paths = glob('/content/split_*.wav')
            sentence1 = ""
            sentence2 = ""
            for i in range(len(paths)):
                path = f'/content/split_{i+1}.wav'
                with open(f"{path}", "rb") as wavfile:
                    input_wav = wavfile.read()
                rate, data = read(io.BytesIO(input_wav))
                bytes_wav = bytes()
                byte_io = io.BytesIO(bytes_wav)
                write(byte_io, rate, data)
                audio = byte_io.read()
                stat1,stat2 = True, True
                
                while(stat1):
                    op1 = query(API_URL_ktp,audio)
                    if 'text' in op1:
                        sentence1+=op1['text']
                        # st.text(op1)
                        stat1 = False
                    else : continue

                while(stat2):
                    op2 = query(API_URL_airesearch,audio)
                    if 'text' in op2:
                        sentence2+=op2['text']
                        # st.text(op2['text'])
                        stat2 = False
                    else : continue  

            with st.expander("ผลลัพท์จากโมเดล Kittipong/wav2vec2-th-vocal-domain"):
                st.write(f"{sentence1}")
            with st.expander("ผลลัพท์จากโมเดล airesearch/wav2vec2-large-xlsr-53-th"):
                st.write(f"{sentence2}")



class input_process:
    def audio_file():

        uploaded_file = st.file_uploader("เลือกไฟล์")
        if uploaded_file is not None:
        # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
            st.audio(bytes_data,'audio/mp3')
            if st.button("ประมวลผล"):
                audio_analysis(bytes_data)

    def url():
        link = st.text_input('ใส่url', 'https://www.youtube.com/watch?v=-BOtfXCIDcs&list=RD-BOtfXCIDcs&start_radio=1')
        st.video(link)
        if st.button("ประมวลผล"):
            yt = YouTube(str(link))
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path='mp3')
            base,ext=os.path.splitext(out_file)

            os.rename(out_file,'song.mp3')

            os.system("spleeter separate -o output/ song.mp3")
            split_file('output/song/vocals.wav')
            # split_file(out_file,'/content/mp3/song.mp3')
            audio_analysis(0)



def main():
    
    with col1:
        option = st.selectbox(
            '🤟รูปแบบข้อมูลเสียงที่ต้องการนำเข้า',
            ('💿ไฟล์เสียง', '🌐url'))

        st.write('Your selected:', option)
        if option == '💿ไฟล์เสียง':
            input_process.audio_file()
        if option == '🌐url':
            os.system('rm -f /content/split_*.wav')
            input_process.url()

if __name__ == '__main__':
    main()
# %%