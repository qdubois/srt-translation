# SRT Translator

A Python script to translate subtitle files (SRT) or extract and translate subtitles from video files (MKV) using a local LLM (via LM Studio) or any OpenAI-compatible API.

## Features

- **Translate SRT files**: Translates English subtitles to a target language.
- **MKV Support**: Automatically extracts the first subtitle track from MKV files using `ffmpeg` before translating.
- **Interactive Language Selection**: Prompts for the target language (defaults to French).
- **Local LLM Support**: Designed to work with local models via LM Studio, but compatible with any OpenAI-like API.

## Prerequisites

- **Python 3.11+**
- **FFmpeg**: Required for processing MKV files.
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **LM Studio** (or another OpenAI-compatible server) running locally.

## Installation

1.  Clone this repository.
2.  Install the required Python packages:

    ```bash
    pip install openai pysrt
    ```

    *Note: The script also includes `uv` metadata headers for easy execution with `uv run`.*

## Usage

1.  Start your local LLM server (e.g., LM Studio) and ensure it is listening (default: `http://localhost:1234/v1`).
2.  Run the script with your input file:

    ```bash
    python translate.py input_movie.mkv
    # or
    python translate.py subtitles.srt
    ```

3.  Enter the target language when prompted (press Enter for French).

### Command Line Arguments

- `input_file`: Path to the input `.srt` or `.mkv` file.
- `--api-url`: URL of the LLM API (default: `http://localhost:1234/v1`).
- `--api-key`: API Key for the server (default: `lm-studio`).
- `--model`: Model identifier to use (default: `qwen/qwen3-8b`).

Example with custom settings:

```bash
python translate.py movie.srt --model "mistral-7b-instruct" --api-url "http://localhost:8000/v1"
```

## Output

The translated subtitles will be saved in the same directory as the input file with the language code appended (e.g., `movie.fr.srt`).
