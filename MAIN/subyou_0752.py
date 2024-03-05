import streamlit as st
import subprocess
import tempfile
import os
import glob
import re
import datetime

def download_video(url, output_path):
    command = f'yt-dlp "{url}" -o "{output_path}"'
    subprocess.run(command, shell=True, check=True)

def download_and_process_subtitles(url, lang_code):
    with tempfile.TemporaryDirectory() as temp_dir:
        command = f'yt-dlp --skip-download --write-subs --write-auto-subs --sub-lang {lang_code} --convert-subs srt "{url}" -o "{temp_dir}/%(title)s.%(ext)s"'
        subprocess.run(command, shell=True, check=True)
        
        subtitle_files = glob.glob(f"{temp_dir}/*.{lang_code}.srt")
        if not subtitle_files:
            return "선택한 언어의 자막 파일을 찾을 수 없습니다."
        
        subtitles = ""
        last_line = None
        for subtitle_file in subtitle_files:
            with open(subtitle_file, "r", encoding="utf-8") as file:
                for line in file:
                    line = re.sub(r'\d+:\d+:\d+.\d+ --> \d+:\d+:\d+.\d+', '', line)
                    line = re.sub(r'^\d+$', '', line, flags=re.MULTILINE)
                    line = re.sub(r'<[^>]+>', '', line)
                    line = re.sub(r'^\s*$', '', line, flags=re.MULTILINE)
                    
                    if line != last_line:
                        subtitles += line
                    last_line = line
            subtitles += "\n\n"
        
        return subtitles.strip()

def remove_duplicate_lines(subtitles):
    lines = subtitles.split("\n")
    unique_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.append(line)
    return "\n".join(unique_lines)

st.title("Subtitle Downloader")

url = st.text_input("Enter video URL:", "")

if "video_file_path" not in st.session_state:
    st.session_state.video_file_path = None

lang_options = {
    "English": "en",
    "Korean": "ko",
    "Japanese": "ja",
    "German": "de",
    "French": "fr",
    "Spanish": "es",
    "Chinese": "zh",
    "Russian": "ru",
    "Arabic": "ar",
    "Portuguese": "pt",
    "Italian": "it",
    "Hindi": "hi",
    "Turkish": "tr",
    "Vietnamese": "vi"
}
selected_lang = st.selectbox("Select subtitle language:", list(lang_options.keys()))

col1, col2 = st.columns(2)

with col1:
    if st.button("Show subtitles"):
        lang_code = lang_options[selected_lang]
        subtitles = download_and_process_subtitles(url, lang_code)
        subtitles = remove_duplicate_lines(subtitles)
        st.text_area("Subtitles:", value=subtitles, height=400, max_chars=None, key="subtitles")
        
        st.download_button(
            label="Download subtitles",
            data=subtitles,
            file_name="subtitles.srt",
            mime="text/plain"
        )
        
        st.video(url)

with col2:
    if st.button("Download video"):
        with st.spinner("Downloading video..."):
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            video_file_path = os.path.join(os.getcwd(), f"video_{current_time}.mp4")
            download_video(url, video_file_path)
            st.session_state.video_file_path = video_file_path
            st.success(f"Video downloaded successfully! File saved at: {video_file_path}")
    
    if st.session_state.video_file_path is not None and os.path.exists(st.session_state.video_file_path):
        with open(st.session_state.video_file_path, "rb") as file:
            video_data = file.read()
        st.download_button(
            label="Download video",
            data=video_data,
            file_name=os.path.basename(st.session_state.video_file_path),
            mime="video/mp4"
        )