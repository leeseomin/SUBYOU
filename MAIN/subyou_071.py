import streamlit as st
import subprocess
import tempfile
import os
import glob
import re

def download_and_process_subtitles(url, lang_code):
    with tempfile.TemporaryDirectory() as temp_dir:
        # yt-dlp를 사용하여 자막 다운로드 및 변환
        command = f'yt-dlp --skip-download --write-subs --write-auto-subs --sub-lang {lang_code} --convert-subs srt "{url}" -o "{temp_dir}/%(title)s.%(ext)s"'
        subprocess.run(command, shell=True, check=True)
        # 변환된 자막 파일 찾기
        subtitle_files = glob.glob(f"{temp_dir}/*.{lang_code}.srt")
        if not subtitle_files:
            return "선택한 언어의 자막 파일을 찾을 수 없습니다."
        # 자막 파일 읽기 및 순수 텍스트 추출
        subtitles = ""
        last_line = None
        for subtitle_file in subtitle_files:
            with open(subtitle_file, "r", encoding="utf-8") as file:
                for line in file:
                    # 시간 코드, 숫자 ID, HTML 태그, 빈 줄 제거
                    line = re.sub(r'\d+:\d+:\d+.\d+ --> \d+:\d+:\d+.\d+', '', line)
                    line = re.sub(r'^\d+$', '', line, flags=re.MULTILINE)
                    line = re.sub(r'<[^>]+>', '', line)
                    line = re.sub(r'^\s*$', '', line, flags=re.MULTILINE)
                    # 중복 줄 제거
                    if line != last_line:
                        subtitles += line
                    last_line = line
                subtitles += "\n\n"
        return subtitles.strip()

def remove_duplicate_lines(subtitles):
    """자막에서 중복된 줄 제거"""
    lines = subtitles.split("\n")
    unique_lines = []
    for line in lines:
        if line not in unique_lines:
            unique_lines.append(line)
    return "\n".join(unique_lines)

# Streamlit UI
st.title("Subtitle Downloader")

# URL 입력
url = st.text_input("Enter video URL:", "")

# 자막 언어 선택
lang_options = {
    "English": "en", "Korean": "ko", "Japanese": "ja", "German": "de",
    "French": "fr", "Spanish": "es", "Chinese": "zh", "Russian": "ru",
    "Arabic": "ar", "Portuguese": "pt", "Italian": "it", "Hindi": "hi",
    "Turkish": "tr", "Vietnamese": "vi"
}
selected_lang = st.selectbox("Select subtitle language:", list(lang_options.keys()))

if st.button("Show subtitles"):
    lang_code = lang_options[selected_lang]
    subtitles = download_and_process_subtitles(url, lang_code)
    subtitles = remove_duplicate_lines(subtitles)
    st.text_area("Subtitles:", value=subtitles, height=400, max_chars=None, key="subtitles")

    # 자막 다운로드 버튼 추가
    st.download_button(
        label="Download subtitles",
        data=subtitles,
        file_name="subtitles.srt",
        mime="text/plain"
    )

    # 영상 플레이어 추가
    video_file = st.video(url)