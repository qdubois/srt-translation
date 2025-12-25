# SRT Translator

A Python script to translate subtitle files (SRT) or extract and translate subtitles from video files (MKV) using a local LLM (via LM Studio) or Google Gemini.

## Features

- **Translate SRT files**: Translates English subtitles to a target language.
- **MKV Support**: Automatically extracts the first subtitle track from MKV files using `ffmpeg` before translating.
- **Interactive Language Selection**: Prompts for the target language (defaults to French).
- **Multi-Provider Support**:
    - **LM Studio**: Work with local models via LM Studio (OpenAI-compatible).
    - **Google Gemini**: Use Google's Gemini models for translation.

## Prerequisites

- **uv**: This script uses `uv` for dependency management.
  - Install instructions: [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
- **FFmpeg**: Required for processing MKV files.
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
- **LM Studio** (if using local models) running locally.
- **Gemini API Key** (if using Gemini).

## Installation

1.  Clone this repository.
2.  That's it! `uv` will handle dependencies automatically when you run the script.

## Usage

### Using LM Studio (Default)

1.  Start your local LLM server (e.g., LM Studio) and ensure it is listening (default: `http://localhost:1234/v1`).
2.  Run the script using `uv run`:

    ```bash
    uv run translate.py input_movie.mkv
    ```

### Using Google Gemini

1.  Set your Gemini API key as an environment variable:
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```
2.  Run the script with the `--provider gemini` flag:
    ```bash
    uv run translate.py input_movie.mkv --provider gemini
    ```

3.  Enter the target language when prompted (press Enter for French).

### Command Line Arguments

- `input_file`: Path to the input `.srt` or `.mkv` file.
- `--provider`: API provider to use (`lm-studio` or `gemini`). Default: `lm-studio`.
- `--target-language`, `-l`: Target language for translation (e.g., `French`, `Spanish`). If not provided, the script will prompt you.
- `--api-url`: URL of the LLM API (for LM Studio).
- `--api-key`: API Key for the server (for LM Studio or Gemini).
- `--model`: Model identifier to use (e.g., `gemini-1.5-flash` for Gemini).
- `--debug`: Enable debug output to print original and translated text.

Example with Gemini and specific language:

```bash
uv run translate.py movie.srt --provider gemini --target-language Spanish
```

Example with custom LM Studio settings:

```bash
uv run translate.py movie.srt --model "mistralai/mistral-small-3.2" --api-url "http://localhost:8000/v1"
```

## Output

The translated subtitles will be saved in the same directory as the input file with the language code appended (e.g., `movie.fr.srt`).
