import gradio as gr
import subprocess
import tempfile
import os
import glob
import re
import datetime
import pyperclip

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

def process_video(url, lang_code):
    subtitles = download_and_process_subtitles(url, lang_code)
    subtitles = remove_duplicate_lines(subtitles)
    return subtitles, gr.update(visible=True), gr.update(visible=True)

def copy_to_clipboard(subtitles):
    pyperclip.copy(subtitles)
    return "Subtitles copied to clipboard!"

def download_video_file(url):
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    video_file_path = os.path.join(os.getcwd(), f"video_{current_time}.mp4")
    download_video(url, video_file_path)
    return f"Video downloaded successfully! File saved at: {video_file_path}"

with gr.Blocks() as demo:
    gr.Markdown("# Subtitle Downloader")
    with gr.Row():
        with gr.Column():
            url = gr.Textbox(label="Enter video URL")
            lang_code = gr.Dropdown(label="Select subtitle language", choices=["en", "ko", "ja", "de", "fr", "es", "zh", "ru", "ar", "pt", "it", "hi", "tr", "vi"])
            submit_btn = gr.Button("Show subtitles")
        with gr.Column():
            subtitles_output = gr.Textbox(label="Subtitles", lines=10)
            copy_btn = gr.Button("Copy to Clipboard")
            copy_output = gr.Textbox(label="Copy Status")
            download_subs_btn = gr.Button("Download subtitles")
            download_video_btn = gr.Button("Download video")
            download_video_output = gr.Textbox(label="Download Status")
    
    def process_video(url, lang_code):
        subtitles = download_and_process_subtitles(url, lang_code)
        subtitles = remove_duplicate_lines(subtitles)
        return subtitles, "Subtitles extracted successfully!", gr.update(visible=True), gr.update(visible=True)

    submit_btn.click(process_video, inputs=[url, lang_code], outputs=[subtitles_output, copy_output, copy_btn, download_subs_btn])
    copy_btn.click(copy_to_clipboard, inputs=subtitles_output, outputs=copy_output)
    
    def download_subtitles(subtitles, url):
        current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        video_file_path = os.path.join(os.getcwd(), f"video_{current_time}.mp4")
        subtitles_file_path = os.path.join(os.path.dirname(video_file_path), f"subtitles_{current_time}.txt")
        with open(subtitles_file_path, "w", encoding="utf-8") as file:
            file.write(subtitles)
        return subtitles_file_path

    download_subs_btn.click(download_subtitles, inputs=[subtitles_output, url], outputs=gr.File(label="Download Subtitles"))
    
    download_video_btn.click(download_video_file, inputs=url, outputs=download_video_output)

demo.launch()
