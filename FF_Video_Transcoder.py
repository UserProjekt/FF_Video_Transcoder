#!/usr/bin/env python3

import os
import subprocess
from tqdm import tqdm
import platform

while True:
    FootageFolderPath = input('Footage Folder Path:')
    if FootageFolderPath.strip():
        break
    else:
        print("Please enter Footage Folder Path...")

while True:
    ProxyFolderPath = input('Proxy Folder Path:')
    if ProxyFolderPath.strip():
        break
    else:
        print("Please enter Proxy Folder Path...")

print()

# read video files
def list_video_files(directory):
    video_extensions = ['.MP4', '.MOV', '.MXF', '.mp4', '.mov', '.mxf']
    video_files = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.startswith("._"):  # Skip macOS metadata files
                continue
            if os.path.splitext(filename)[1] in video_extensions:
                video_files.append(os.path.join(dirpath, filename))
    return video_files

# enlarge the Terminal window
current_platform = platform.system()
if current_platform == "Darwin":  # macOS
    script = """
    tell application "Terminal"
        activate
        set bounds of front window to {0, 0, 1280, 720}  
    end tell
    """
    os.system(f"osascript -e '{script}'")

# create Date folder in Proxy Folder
DateFolderNameList = [DateFolder.name for DateFolder in os.scandir(FootageFolderPath) if DateFolder.is_dir()]
ProxyDateFolderPathList = []
TotalDateFolders = len(DateFolderNameList)

# define folder progress bar
fbar = tqdm(total=TotalDateFolders, position=1, desc="------- Completed Date Folders", unit="folder", ncols=30, bar_format='{l_bar} {n_fmt}/{total_fmt} Folders')
for DateFolderName in DateFolderNameList:
    ProxyDateFolderPath = os.path.join(ProxyFolderPath, DateFolderName)
    os.makedirs(ProxyDateFolderPath, exist_ok=True)  # added exist_ok to avoid errors if folder already exists
    ProxyDateFolderPathList.append(ProxyDateFolderPath)

# transcoding
for DateFolderName, ProxyDateFolderPath in zip(DateFolderNameList, ProxyDateFolderPathList):
    FootageDateFolderPath = os.path.join(FootageFolderPath, DateFolderName)
    VideoFilePathList = list_video_files(FootageDateFolderPath)
    for VideoFilePath in VideoFilePathList:
        OutputName = os.path.splitext(os.path.basename(VideoFilePath))[0] + ".mov"
        OutputPath = os.path.join(ProxyDateFolderPath, OutputName)

        # getting the total number of frames in the video
        ffprobe_cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=nb_frames", "-of", "default=nokey=1:noprint_wrappers=1", VideoFilePath]
        total_frames = int(subprocess.check_output(ffprobe_cmd).decode('utf-8').strip())

        # get the video filename
        VideoFilename = os.path.basename(VideoFilePath)

        # Define the video progress bar here
        # Left side padding
        max_length_left = 50
        desc_text = "File: " + VideoFilename
        desc_text = desc_text.ljust(max_length_left)  # This pads the string to the desired length

        # Right side padding
        FrameSpeedpd = 6  # frame/s padding
        rate_fmt = " [{rate_fmt:>" + str(FrameSpeedpd) + "}]"
        FrameLpd = 8      # frame left padding
        FrameRpd = 8  # frame right padding

        frame_fmt = "{n:>" + str(FrameLpd) + "}" + "/{total:<" + str(FrameRpd) + "}"

        # define transcoding progress bar
        pbar = tqdm(total=total_frames, position=0, desc=desc_text + "Progress", unit="frame", dynamic_ncols=True, bar_format='{l_bar}{bar}| [{elapsed}<{remaining}]  ' + frame_fmt + rate_fmt)

        #display fbar
        fbar.refresh()

        #setting codec for different OS
        if platform.system() == "Windows":
            vcodec = "hevc_nvenc"  # for HEVC encoding
        elif platform.system() == "Darwin":
            vcodec = "hevc_videotoolbox"
        else:
            vcodec = "libx265"  # Default codec for Linux and other platforms

        # start the ffmpeg process and monitor its output
        command = ["ffmpeg", "-y", "-i", VideoFilePath, "-c:v", vcodec, "-b:v", "5000k", "-pix_fmt", "yuv420p", "-c:a", "libmp3lame", "-b:a", "160k", "-progress", "-", OutputPath]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1, encoding="utf-8")

        # use tqdm to display the progress bar
        for line in process.stdout:
            if "frame=" in line:
                try:
                    current_frame_str = line.split('frame=')[1].split(' ')[0].strip()
                    if current_frame_str.isdigit():
                        current_frame = int(current_frame_str)
                        pbar.update(current_frame - pbar.n)  # Update the progress bar with the number of new frames processed
                except ValueError:
                    continue  # skip the problematic line
        pbar.close()
        process.wait()
    fbar.update(1)
fbar.close()
