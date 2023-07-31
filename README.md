# FF_Video_Transcoder
This is a python script using FFmpeg for transcoding in video production. 
It's set for Full High Definition (FHD) video with H.265 encoding, 4:2:0 chroma subsampling, 8-bit color depth, and a video bitrate of 5Mbps,audio channel are matched source file,bitrate of 128kbps per channel. These settings are optimized for hardware decoding and systems with low I/O performance. Reduced file size is also better for transfer and storage.

[FFmpeg hardware encoding/decoding information](https://trac.ffmpeg.org/wiki/HWAccelIntro)


# Installation
This script requires following to be installed

    Python 3.10
    ffmpeg
    ffprobe

FFmpeg for transcoding,On macOS, This script uses the 'videotoolbox' for hardware encoding on modern Macs, whether they're Apple Silicon or Intel. On Windows, it uses Nvidia's NVENC to do the job.

ffprobe is required to get the total number of frames in the video for an accurate progress bar representation.

## MacOS
You can install FFmpeg using [Homebrew](https://brew.sh) 

    #using Homebrew (https://brew.sh)
    brew install ffmpeg

When you use Homebrew to install FFmpeg (brew install ffmpeg), it will typically install the ffprobe tool alongside it, as ffprobe is part of the FFmpeg suite. So, if you've already installed FFmpeg using Homebrew, you should already have access to ffprobe.
You can check its presence by typing ffprobe -version in the terminal. If it returns a version number and some details, then you have it installed.

Alternatively, you can download both from [here](https://ffmpeg.org/download.html#build-mac), and add them to PATH.

## Windows
You can install FFmpeg using package managers:

    #using Chocolatey (https://chocolatey.org/)
    choco install ffmpeg

    #using Scoop (https://scoop.sh/)
    scoop install ffmpeg

ffprobe already in FFmpeg suite

Alternatively, you can download both from [here](https://ffmpeg.org/download.html#build-mac), and add them to PATH.

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
Upon running this script, the terminal prompts the user to provide the paths for the footage folder and the proxy folder. 

After the paths are inputted, the script recreate the date-based folder structure within the Proxy folder, It then proceeds to transcode each '.MP4', '.MOV', '.MXF', '.mp4', '.mov', and '.mxf' video file into '.mov' format.

<img width="1392" alt="Screenshot 2023-07-28 at 22 08 14" src="https://github.com/UserProjekt/FF_Video_Transcoder/assets/78477492/05d306ce-f631-4fb6-a906-f8fc0fb974da">
The script actively informs you of the video currently being transcoded, providing details on the ongoing process, including the transcoding progress, elapsed time, remaining time, number of frames, speed, and total Progress.
