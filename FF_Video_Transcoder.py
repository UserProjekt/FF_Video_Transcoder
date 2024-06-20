#!/usr/bin/env python3
import os
import subprocess
from tqdm import tqdm
import platform
import json
import re

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

# Path to the Courier TrueType font on Windows, used for drawing text on the video.
font_win_path = r"C:\Windows\Fonts\Cour.ttf"

# Prompts the user to choose the codec until a valid choice is made
while True:
    print()
    print("Choose the video codec:")
    print("1. HEVC")
    print("2. ProRes Proxy")
    print("3. Auto (Choose ProRes if footage has more than 4 audio streams)")
    choice = input("Enter the number of your choice: ")
    if choice in ["1", "2", "3"]:
        break
    else:
        print("Invalid choice. Please enter 1 for HEVC, 2 for ProRes, or 3 for Auto.")
print()

# Video codec specifics
if platform.system() == "Windows":
    font = font_win_path.replace('\\', '/').replace(':', '\\:')
elif platform.system() == "Darwin":
    font = "Courier New"

def determine_codec(metadata):
    audio_streams = sum(1 for track in metadata["media"]["track"] if track["@type"] == "Audio")
    return "2" if audio_streams > 4 else "1"

class VideoTranscoder:
    # Initializes VideoTranscoder with directory paths for footage and proxies.
    def __init__(self, FootageFolderPath, ProxyFolderPath):
        self.FootageFolderPath = FootageFolderPath
        self.ProxyFolderPath = ProxyFolderPath

    # Extracts metadata from the footage file using mediainfo.
    def extract_metadata(self):
        command = [
            "mediainfo", "--Output=JSON", self.FootageFile
        ]

        try:
            output = subprocess.check_output(command).decode("utf-8")
            metadata = json.loads(output)

            timecode = None
            total_frames = None
            frame_rate = None

            # Checks if timecode exists in the metadata.
            # First pass to prioritize Video track for FrameCount and FrameRate
            if "media" in metadata and "track" in metadata["media"]:
                for track in metadata["media"]["track"]:
                    if track["@type"] == "Video":
                        if "FrameCount" in track:
                            total_frames = int(track["FrameCount"])
                        if "FrameRate" in track:
                            frame_rate = round(float(track["FrameRate"]))
                        break  # Stop after finding the Video track

            # Second pass to get TimeCode from any track and fallback for FrameCount and FrameRate
            for track in metadata["media"]["track"]:
                if timecode is None and "TimeCode_FirstFrame" in track:
                    timecode = track["TimeCode_FirstFrame"]
                if total_frames is None and "FrameCount" in track:
                    total_frames = int(track["FrameCount"])
                if frame_rate is None and "FrameRate" in track:
                    frame_rate = round(float(track["FrameRate"]))

            if frame_rate not in [30, 60] and timecode:
                # Convert drop-frame timecode to non-drop-frame timecode if necessary.
                if ";" in timecode:
                    timecode = timecode.replace(';', ':')
                # Escapes the colons in the timecode.
                timecode = timecode.replace(':', '\\:')
            elif timecode:
                # Escapes both colons and semicolons in the timecode.
                timecode = timecode.replace(':', '\\:').replace(';', '\\;')
            
            return total_frames, timecode, frame_rate, metadata

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
            return None, None, None, None

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
                    self.footage_name = os.path.basename(footage_file)
                    self.ProxyFile = proxy_file
                    self.total_frames, self.timecode, self.frame_rate, self.metadata = self.extract_metadata()
                    yield self
        
    # Transcodes a video using FFmpeg, displaying the progress with tqdm.
    def ffmpeg_tqdm(self):
        if choice == "3":
            codec_choice = determine_codec(self.metadata)
        else:
            codec_choice = choice

        if platform.system() == "Windows":
            if codec_choice == "1":
                vcodec = "hevc_nvenc"
                codec_specific_params = []
            elif codec_choice == "2":
                vcodec = "prores_ks"
                codec_specific_params = [
                    "-profile:v", "0",       # Prores Proxy
                    "-quant_mat", "0",       # Sets the quantization matrix to the default
                    "-qscale:v", "4",        # Sets the quality scale to 4 (good balance between quality and file size)
                    "-color_range", "1",     # Sets color range / data level flag
                    "-colorspace", "1",      # Sets color space flag
                    "-color_trc", "1",       # Sets OETF flag
                    "-color_primaries", "1", # Sets color primaries flag
                ]
        elif platform.system() == "Darwin":
            if codec_choice == "1":
                vcodec = "hevc_videotoolbox"
                codec_specific_params = []
            elif codec_choice == "2":
                vcodec = "prores_videotoolbox"
                codec_specific_params = [
                    "-profile:v", "0",       # Prores Proxy
                    "-color_range", "1",     # Sets color range / data level flag
                    "-colorspace", "1",      # Sets color space flag
                    "-color_trc", "1",       # Sets OETF flag
                    "-color_primaries", "1", # Sets color primaries flag
                ]

        command = [
            "ffmpeg",
            "-y",  # Overwrite output file without asking
            "-i", self.FootageFile,  # Input file
            "-vf", (f"scale='min(1920,iw)':-1,"f"drawtext=fontfile='{font}':fontsize=40:fontcolor=white@0.9:box=1:boxcolor=black@0.55:boxborderw=10:x=30:y=30:text='{self.footage_name}',"f"drawtext=fontfile='{font}':fontsize=40:fontcolor=white@0.9:box=1:boxcolor=black@0.55:boxborderw=10:x=w-tw-30:y=30:timecode='{self.timecode}':rate={self.frame_rate}:tc24hmax=1"),
            "-c:v", vcodec,
            "-c:a", "libmp3lame",  # Audio codec
            "-b:a", "160k",        # Audio bitrate
            "-map", "0:v",         # Maps the video stream
            "-map", "0:a",         # Maps the audio streams
            "-progress", "pip2",   # Output progress
            self.ProxyFile
    ]
        # Adds codec-specific parameters
        command.extend(codec_specific_params)

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding='utf-8')

        # Defines transcoding progress bar
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

        frame_re = re.compile(r'frame=\s*(\d+)')

        while True:
            line = process.stderr.readline()
            if line == "" and process.poll() is not None:
                break

            match = frame_re.search(line)
            if match:
                try:
                    current_frame = int(match.group(1))
                    pbar.update(current_frame - pbar.n)  # Update the progress bar with the number of new frames processed
                except ValueError:
                    continue  # Skip the problematic line

        process.wait()
        
        # Ensures the progress bar is updated to the total frames if the process completes successfully
        if process.returncode == 0:
            pbar.n = self.total_frames
            pbar.last_print_n = self.total_frames
            pbar.update(0)
        else:
            print(f"Error during transcoding: {self.FootageFile}")

        pbar.close()

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
        vbar.update(1)  # Update the total progress bar after processing each file

    vbar.close()
