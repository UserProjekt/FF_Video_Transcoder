# FF_Video_Transcoder
This is a Python script using FFmpeg for transcoding in video production. It is designed for Full High Definition (FHD) video with options for H.265 (4:2:0, 8-bit, 5Mbps) or ProRes Proxy. The script includes filename and timecode burn-in, and it matches the audio channels of the source file, encoding them as MP3 with 128Kbps per track. These settings are optimized for hardware decoding and systems with low I/O performance. The reduced file size also makes it more efficient for transfer and storage.

Due to an issue with Adobe Premiere, which cannot use hardware decoding for 4:2:0 8-bit H.265 with 8 audio tracks (Sony XAVC-I codec), an auto mode has been implemented to choose the codec based on the number of audio tracks. The script will prompt you to select the preferred codec.

[FFmpeg hardware encoding/decoding information](https://trac.ffmpeg.org/wiki/HWAccelIntro)

# Installation
This script requires following to be installed

    Python 3
    tqdm
    ffmpeg 6.1.1
    mediainfo cli

Irrespective of how Python 3 was installed (e.g., via Homebrew, from python.org)Please ensure Python 3 is in the PATH.

'tqdm' is not a part of the standard library in Python 3. Instead, it's an external library that provides a fast, extensible progress bar for loops and other computations.

    pip3 install tqdm

FFmpeg for transcoding, on macOS, This script uses the 'videotoolbox' for hardware encoding on modern Macs, whether they're Apple Silicon or Intel. On Windows, it uses Nvidia's NVENC for the job.

## MacOS
Install FFmpeg 

    #using Homebrew (https://brew.sh)
    brew install ffmpeg
    
Alternatively, you can download FFmpeg from [here](https://ffmpeg.org/download.html#build-mac), and add it to PATH.

## Windows
You can install FFmpeg using package managers:

    #using Chocolatey (https://chocolatey.org/)
    choco install ffmpeg

    #using Scoop (https://scoop.sh/)
    scoop install ffmpeg

Alternatively, you can download FFmpeg from [here](https://ffmpeg.org/download.html#build-mac), download MediaInfo CLI from its official website: [MediaArea - MediaInfo](https://mediaarea.net/en/MediaInfo/Download/Windows),and then add them to the PATH.

# Folder Structure
The industray standard footage folder structure is outlined below. **Please ensure that the date-specific folders (e.g., 'Shooting Day 1', 'Shooting Day 2') are situated directly beneath the 'Footage' folder.**
- 📁 Production
  - 📁 Footage
    - 📁 Shooting Day 1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting Day 2
      - 📁 A002_0210Z9

  
In our workflow,We place the Proxy folder alongside the Footage folder,feel free to put it wherever you like
- 📁 Production
  - 📁 Proxy
  - 📁 Footage
    - 📁 Shooting Day 1
      - 📁 A001_0210Z9
      - 📁 B001_029AC3
    - 📁 Shooting Day 2
      - 📁 A002_0210Z9

# Usage

If you're on macOS, ensure that the script is made executable.
Navigate to the directory containing the script and type:

    chmod +x FF_Video_Transcoder.py
    
Upon running this script, the terminal prompts the user to provide the paths for the footage folder and the proxy folder. 

After the paths are inputted, the script recreate the date-based folder structure within the Proxy folder, It then proceeds to transcode each '.MP4', '.MOV', '.MXF', '.mp4', '.mov', and '.mxf' video file into '.mov' format.

<img width="1392" alt="Screenshot 2023-07-28 at 22 08 14" src="https://github.com/UserProjekt/FF_Video_Transcoder/assets/78477492/05d306ce-f631-4fb6-a906-f8fc0fb974da">
The script actively informs you of the video currently being transcoded, providing details on the ongoing process, including the transcoding progress, elapsed time, remaining time, number of frames, speed, and total Progress.
