import pandas as pd
import urllib.request
import os
import zipfile
import shutil
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

# load file with labels
df = pd.read_csv('training/labels.csv')

# config remote host and local import dir
BASE_URL = ""
OUTPUT_DIR = "./training/files"

# create import dir if not exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

total = len(df)
for i, participant_id in enumerate(df['Participant_ID'], 1):
    pid = str(participant_id)
    zip_name = f"{pid}_P.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_name)
    audio_filename = f"{pid}_AUDIO.wav"
    audio_dest = os.path.join(OUTPUT_DIR, audio_filename)

    # ignore fiels if exist locally
    if os.path.exists(audio_dest):
        print(f"[{i}/{total}] Ignore {pid} — files exists")
        continue

    # download archive
    url = f"{BASE_URL}/{zip_name}"
    try:
        print(f"[{i}/{total}] Downloading {zip_name} ...", flush=True)
        urllib.request.urlretrieve(url, zip_path)
    except Exception as e:
        print(f"[{i}/{total}] [x] Cannot download {pid}: {e}")
        continue

    # unpack archive
    extract_dir = os.path.join(OUTPUT_DIR, f"{pid}_P")
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
        print(f"[{i}/{total}] [v] Archive extracted into {extract_dir}")
    except Exception as e:
        print(f"[{i}/{total}] [x] Cannot extract {pid}: {e}")
        continue

    # find WAV file
    audio_source = None
    for root, dirs, files in os.walk(extract_dir):
        for f in files:
            if f == audio_filename:
                audio_source = os.path.join(root, f)
                break

    if audio_source is None:
        print(f"[{i}/{total}] [x] Not found {audio_filename} in archive.")
        continue

    # move only audio file upper one dir
    shutil.move(audio_source, audio_dest)
    print(f"[{i}/{total}] [v] Moved: {audio_dest}")

    # clean - remove archive and unused files
    os.remove(zip_path)
    shutil.rmtree(extract_dir)
    print(f"[{i}/{total}] [v] Clean")

print("\[v] Done!")