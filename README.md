# SRT Translator

A Python script to translate subtitle files (SRT) or extract and translate subtitles from video files (MKV) using a local LLM (via LM Studio) or any OpenAI-compatible API.

## Features

- **Translate SRT files**: Translates English subtitles to a target language.
- **MKV Support**: Automatically extracts the first subtitle track from MKV files using `ffmpeg` before translating.
- **Interactive Language Selection**: Prompts for the target language (defaults to French).
- **Local LLM Support**: Designed to work with local models via LM Studio, but compatible with any OpenAI-like API.

## Prerequisites

- **uv**: This script uses `uv` for dependency management.
  - Install instructions: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- **FFmpeg**: Required for processing MKV files.
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **LM Studio** (or another OpenAI-compatible server) running locally.

## Installation

1.  Clone this repository.
2.  That's it! `uv` will handle dependencies automatically when you run the script.

## Usage

1.  Start your local LLM server (e.g., LM Studio) and ensure it is listening (default: `http://localhost:1234/v1`).
2.  Run the script using `uv run`:

    ```bash
    uv run translate.py input_movie.mkv
    # or
    uv run translate.py subtitles.srt
    ```

3.  Enter the target language when prompted (press Enter for French).

### Command Line Arguments

- `input_file`: Path to the input `.srt` or `.mkv` file.
- `--api-url`: URL of the LLM API (default: `http://localhost:1234/v1`).
- `--api-key`: API Key for the server (default: `lm-studio`).
- `--model`: Model identifier to use (default: `qwen/qwen3-8b`).
- `--debug`: Enable debug output to print original and translated text.

Example with custom settings:

```bash
uv run translate.py movie.srt --model "mistralai/mistral-small-3.2" --api-url "http://localhost:8000/v1"
```

## Output

The translated subtitles will be saved in the same directory as the input file with the language code appended (e.g., `movie.fr.srt`).
