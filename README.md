# DAIC-WOZ Database Downloader

A script for batch-downloading audio files from the [DAIC-WOZ](https://dcapswoz.ict.usc.edu/) (Distress Analysis Interview Corpus – Wizard of Oz) database, a dataset used for depression and distress analysis research.

## How it works

The script reads a list of participant IDs from `training/labels.csv`, downloads the corresponding ZIP archive for each participant from the remote host, extracts only the WAV audio file, and removes the archive and any other extracted content.

Files that already exist locally are skipped, so the script is safe to re-run after interruptions.

## Prerequisites

- Python 3
- `pandas`

```bash
pip install pandas
```

## Setup

### 1. Obtain access to DAIC-WOZ

Request access to the dataset at [https://dcapswoz.ict.usc.edu/](https://dcapswoz.ict.usc.edu/). After approval you will receive credentials and a download URL.

### 2. Prepare `training/labels.csv`

The CSV must contain at least a `Participant_ID` column. The file provided with the dataset (`train_split_Depression_AVEC2017.csv` or similar) can be used directly.

A sample file is included as `labels.csv.example` — copy and rename it as a starting point:

```bash
cp labels.csv.example training/labels.csv
```

```
training/
└── labels.csv
```

### 3. Set `BASE_URL` in the script

Open `download_files.py` and set `BASE_URL` to the base URL you received with your dataset access:

```python
BASE_URL = "https://<your-download-host>/<path>"
```

## Usage

```bash
python download_files.py
```

Progress is printed for each participant:

```
[1/107] Downloading 300_P.zip ...
[1/107] [v] Archive extracted into ./training/files/300_P
[1/107] [v] Moved: ./training/files/300_AUDIO.wav
[1/107] [v] Clean
[2/107] Ignore 301 — files exists
...
[v] Done!
```

## Output

All WAV files are saved to `./training/files/`:

```
training/
└── files/
    ├── 300_AUDIO.wav
    ├── 301_AUDIO.wav
    └── ...
```

## Notes

- **SSL warning:** Certificate verification is explicitly disabled in the script (`ssl._create_unverified_context`). This is an intentional workaround for the DAIC-WOZ download server, but it is a security risk — it makes the connection vulnerable to man-in-the-middle attacks. Do not reuse this pattern in other contexts.
- The `training/labels.csv` file is listed in `.gitignore` and should not be committed to the repository.
