import pandas as pd
import urllib.request
import os
import zipfile
import shutil
import ssl
import sys

BASE_URL = ""
LABELS_CSV = "training/labels.csv"
OUTPUT_DIR = "training/files"


def validate_config():
    errors = []

    if not BASE_URL:
        errors.append("BASE_URL is not set. Open download_files.py and set BASE_URL to the download server address.")

    if not os.path.exists(LABELS_CSV):
        errors.append(f"Labels file not found: {LABELS_CSV}. Copy labels.csv.example to {LABELS_CSV} and fill it with participant data.")

    if errors:
        for err in errors:
            print(f"[x] {err}")
        sys.exit(1)


def load_labels():
    try:
        df = pd.read_csv(LABELS_CSV)
    except Exception as e:
        print(f"[x] Cannot read {LABELS_CSV}: {e}")
        sys.exit(1)

    if "Participant_ID" not in df.columns:
        print(f"[x] Column 'Participant_ID' not found in {LABELS_CSV}.")
        print(f"[x] Available columns: {', '.join(df.columns)}")
        sys.exit(1)

    if df.empty:
        print(f"[x] {LABELS_CSV} contains no rows.")
        sys.exit(1)

    return df


def download_participant(pid, i, total):
    zip_name = f"{pid}_P.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_name)
    audio_filename = f"{pid}_AUDIO.wav"
    audio_dest = os.path.join(OUTPUT_DIR, audio_filename)
    extract_dir = os.path.join(OUTPUT_DIR, f"{pid}_P")

    if os.path.exists(audio_dest):
        print(f"[{i}/{total}] [-] {pid} — already exists")
        return True

    url = f"{BASE_URL}/{zip_name}"
    try:
        print(f"[{i}/{total}] [>] Downloading {zip_name} ...", flush=True)
        urllib.request.urlretrieve(url, zip_path)
    except urllib.error.HTTPError as e:
        print(f"[{i}/{total}] [x] HTTP {e.code} for {pid}: {e.reason}")
        return False
    except urllib.error.URLError as e:
        print(f"[{i}/{total}] [x] Cannot reach server for {pid}: {e.reason}")
        return False
    except Exception as e:
        print(f"[{i}/{total}] [x] Download failed for {pid}: {e}")
        return False

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)
    except zipfile.BadZipFile:
        print(f"[{i}/{total}] [x] Downloaded file is not a valid ZIP for {pid}.")
        _cleanup(zip_path=zip_path)
        return False
    except Exception as e:
        print(f"[{i}/{total}] [x] Extraction failed for {pid}: {e}")
        _cleanup(zip_path=zip_path)
        return False

    audio_source = None
    for root, _, files in os.walk(extract_dir):
        for f in files:
            if f == audio_filename:
                audio_source = os.path.join(root, f)
                break

    if audio_source is None:
        print(f"[{i}/{total}] [x] {audio_filename} not found in archive.")
        _cleanup(zip_path=zip_path, extract_dir=extract_dir)
        return False

    shutil.move(audio_source, audio_dest)
    print(f"[{i}/{total}] [v] {audio_dest}")

    _cleanup(zip_path=zip_path, extract_dir=extract_dir)
    return True


def _cleanup(zip_path=None, extract_dir=None):
    if zip_path and os.path.exists(zip_path):
        os.remove(zip_path)
    if extract_dir and os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)


def main():
    ssl._create_default_https_context = ssl._create_unverified_context  # noqa: S501

    validate_config()
    df = load_labels()
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total = len(df)
    ok = 0
    failed = 0

    for i, participant_id in enumerate(df["Participant_ID"], 1):
        success = download_participant(str(participant_id), i, total)
        if success:
            ok += 1
        else:
            failed += 1

    print(f"\n[v] Done: {ok} ok, {failed} failed, {total} total.")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
