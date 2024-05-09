#!/usr/bin/env python3
import os
import subprocess
from tqdm import tqdm
import platform
import json

# Cleans the input path by removing escaped characters and quotes.
def clean_path_input(path):
    # Removes escape characters from spaces.
    path = path.replace("\\ ", " ")
    # Removes escape characters from hash symbols.
    path = path.replace("\\#", "#")
    # Removes quotes around the path (if any).
    path = path.strip('" ').strip()
    return path

while True:
    FootageFolderPath = input('Footage Folder Path:')
    # Corrects the path input for any escaped spaces.
    FootageFolderPath = clean_path_input(FootageFolderPath)
    if FootageFolderPath.strip():
        break
    else:
        print("Please enter Footage Folder Path...")

while True:
    ProxyFolderPath = input('Proxy Folder Path:')
    # Corrects the path input for any escaped spaces.
    ProxyFolderPath = clean_path_input(ProxyFolderPath)
    if ProxyFolderPath.strip():
        break
    else:
        print("Please enter Proxy Folder Path...")

# Enlarges the Terminal window depending on the platform.
current_platform = platform.system()
if current_platform == "Darwin":  # macOS
    script = """
    tell application "Terminal"
        activate
        set bounds of front window to {0, 0, 1280, 720}  
    end tell
    """
    os.system(f"osascript -e '{script}'")

# Sets the codec based on the operating system.
if platform.system() == "Windows":
    vcodec = "hevc_nvenc"  # for HEVC encoding.
elif platform.system() == "Darwin":
    vcodec = "hevc_videotoolbox"
else:
    vcodec = "libx265"  # Default codec for other platforms.  

class VideoTranscoder:
    # Initializes VideoTranscoder with directory paths for footage and proxies.
    def __init__(self, FootageFolderPath, ProxyFolderPath):
        self.FootageFolderPath = FootageFolderPath
        self.ProxyFolderPath = ProxyFolderPath

    # Extracts metadata from the footage file using ffprobe.
    def extract_metadata(self):
        command = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", self.FootageFile
        ]

        try:
            output = subprocess.check_output(command).decode("utf-8")
            metadata = json.loads(output)

            timecode = None
            total_frames = None
            frame_rate = None

            # Checks if timecode exists in format tags.
            if "format" in metadata and "tags" in metadata["format"]:
                format_tags = metadata["format"]["tags"]
                if "timecode" in format_tags:
                    timecode = format_tags["timecode"]

            # Checks if timecode exists in any of the stream tags.
            if "streams" in metadata:
                for stream in metadata["streams"]:
                    if "tags" in stream and "timecode" in stream["tags"]:
                        timecode = stream["tags"]["timecode"]
                    if "codec_type" in stream and stream["codec_type"] == "video":
                        if "nb_frames" in stream:
                            total_frames = int(stream["nb_frames"])
                        elif "duration_ts" in stream:
                            total_frames = int(stream["duration_ts"])
                        if "r_frame_rate" in stream:
                            frame_rate = round(eval(stream["r_frame_rate"]))

            # Escapes the colons in the timecode.
            timecode = timecode.replace(':', '\\:')
            
            return total_frames, timecode, frame_rate

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return None, None, None

    # Iterates through the footage directory, generating a corresponding structure in the proxy directory.
    def iteration(self):
        for root, dirs, files in os.walk(self.FootageFolderPath):
            for file in files:
                if file.lower().endswith((".mp4", ".mov", ".mxf")):
                    footage_file = os.path.join(root, file)
                    relative_path = os.path.relpath(root, self.FootageFolderPath)
                    path_parts = relative_path.split(os.sep)
                    if len(path_parts) > 0:
                        subfolder = path_parts[0]
                    else:
                        subfolder = ""
                    proxy_dir = os.path.join(self.ProxyFolderPath, subfolder)
                    os.makedirs(proxy_dir, exist_ok=True)
                    proxy_file = os.path.join(proxy_dir, os.path.splitext(file)[0] + ".mov")
                    self.FootageFile = footage_file
                    self.ProxyFile = proxy_file
                    self.total_frames, self.timecode, self.frame_rate = self.extract_metadata()
                    yield self
        
    # Transcodes a video using FFmpeg, displaying the progress with tqdm.
    def ffmpeg_tqdm(self):
        command = [
        "ffmpeg",
        "-y",  # Overwrite output file without asking
        "-i", self.FootageFile,  # Input file
        "-vf", "scale='min(1920,iw)':-1,drawtext=fontfile=/System/Library/Fonts/Supplemental/Courier New.ttf:fontsize=40:fontcolor=white@0.9:box=1:boxcolor=black@0.55:boxborderw=10:x=30:y=30:text='{}',drawtext=fontfile=/System/Library/Fonts/Supplemental/Courier New.ttf:fontsize=40:fontcolor=white@0.9:box=1:boxcolor=black@0.55:boxborderw=10:x=w-tw-30:y=30:timecode='{}':rate={}:tc24hmax=1".format(os.path.basename(self.FootageFile), self.timecode, self.frame_rate),
        "-c:v", vcodec,
        "-b:v", "5000k",  # Video bitrate
        "-pix_fmt", "yuv420p",  # Pixel format
        "-c:a", "libmp3lame",  # Audio codec
        "-b:a", "160k",  # Audio bitrate
        "-map", "0:v",  # Map video stream
        "-map", "0:a",  # Map audio stream
        "-progress", "-",  # Output progress
        self.ProxyFile
    ]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

        # Defines a transcoding progress bar
        # Left side padding
        max_length_left = 50
        desc_text = "File: " + os.path.basename(self.FootageFile)
        desc_text = desc_text.ljust(max_length_left)  # This pads the string to the desired length

        # Right side padding
        FrameSpeedpd = 13  # frame/s padding
        rate_fmt = "[" + "{rate_fmt:>" + str(FrameSpeedpd) + "}]"

        FrameLpd = 8      # frame left padding
        FrameRpd = 9      # frame right padding
        frame_fmt = "{{n:>{FrameLpd}}}/{{total:<{FrameRpd}}}".format(FrameLpd=FrameLpd, FrameRpd=FrameRpd)

        pbar = tqdm(total=self.total_frames, position=0, desc=desc_text + "Progress", unit="frame", dynamic_ncols=True, bar_format='{l_bar}{bar}| [{elapsed}<{remaining}]  ' + frame_fmt + rate_fmt)

        # Uses tqdm to display the progress bar
        for line in process.stdout:
            if "frame=" in line:
                try:
                    current_frame_str = line.split('frame=')[1].split(' ')[0].strip()
                    if current_frame_str.isdigit():
                        current_frame = int(current_frame_str)
                        pbar.update(current_frame - pbar.n)  # Updates the progress bar with the number of new frames processed
                except ValueError:
                    continue  # Skips the problematic line
        pbar.close()
        process.wait()
        if process.returncode == 0:
            vbar.update(1)
        else:
            print(f"Error during transcoding: {self.FootageFile}")

# Caculates the number of total Video files
TotalVideoFiles = 0
for root, dirs, files in os.walk(FootageFolderPath):
    for file in files:
        if file.lower().endswith((".mp4", ".mov", ".mxf")):
            TotalVideoFiles += 1

if __name__ == "__main__":
    Transcoder = VideoTranscoder(FootageFolderPath, ProxyFolderPath)
    vbar = tqdm(total=TotalVideoFiles, position=1, desc="-------- Completed Video Files", bar_format='{l_bar} {n_fmt}/{total_fmt}')
    for Transcoding in Transcoder.iteration():
        Transcoding.ffmpeg_tqdm()
    vbar.close()