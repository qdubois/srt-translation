# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
#     "pysrt",
# ]
# ///

import argparse
import sys
import os
import shutil
import subprocess
from openai import OpenAI
import pysrt

def check_ffmpeg():
    """Checks if ffmpeg is installed."""
    if shutil.which("ffmpeg") is None:
        print("Error: ffmpeg is not installed. Please install it to process MKV files.", file=sys.stderr)
        if sys.platform == "darwin":
            print("You can install it using Homebrew: brew install ffmpeg", file=sys.stderr)
        elif sys.platform == "linux":
            print("You can install it using apt: sudo apt install ffmpeg", file=sys.stderr)
        return False
    return True

def extract_subtitles(mkv_path):
    """Extracts the first subtitle track from an MKV file to an SRT file."""
    base_name = os.path.splitext(mkv_path)[0]
    srt_path = f"{base_name}.srt"
    
    cmd = ["ffmpeg", "-y", "-i", mkv_path, "-map", "0:s:0", srt_path]
    
    print(f"Extracting subtitles from {mkv_path}...")
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return srt_path
    except subprocess.CalledProcessError as e:
        print(f"Error extracting subtitles: {e}", file=sys.stderr)
        return None

def translate_text(client, text, target_language="French", model="local-model"):
    """
    Translates text from English to the target language using the LM Studio API.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"You are a professional subtitle translator. Translate the following English subtitle text to {target_language}. Maintain the tone and context. Return ONLY the translated text, no explanations or quotes."},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error translating line '{text}': {e}", file=sys.stderr)
        return text  # Return original text on failure

def main():
    parser = argparse.ArgumentParser(description="Translate SRT or MKV file from English to a target language using LM Studio.")
    parser.add_argument("input_file", help="Path to the input file (e.g., movie.srt or movie.mkv).")

    parser.add_argument("--api-url", default="http://localhost:1234/v1", help="LM Studio API URL (default: http://localhost:1234/v1)")
    parser.add_argument("--api-key", default="lm-studio", help="API Key (default: lm-studio)")
    parser.add_argument("--model", default="qwen/qwen3-8b", help="Model identifier to use in LM Studio")

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # Language prompt
    target_language = input("Target language [French]: ").strip()
    if not target_language:
        target_language = "French"

    input_file = args.input_file
    
    # Handle MKV
    if input_file.lower().endswith('.mkv'):
        if not check_ffmpeg():
            sys.exit(1)
        extracted_srt = extract_subtitles(input_file)
        if not extracted_srt:
            print("Failed to extract subtitles or no subtitles found.", file=sys.stderr)
            sys.exit(1)
        input_file = extracted_srt

    # Determine output filename
    if target_language.lower() == "french":
        lang_code = "fr"
    else:
        lang_code = target_language.lower()[:3]

    if input_file.endswith('.en.srt'):
        output_file = input_file[:-7] + f'.{lang_code}.srt'
    elif input_file.endswith('.srt'):
        output_file = input_file[:-4] + f'.{lang_code}.srt'
    else:
        output_file = input_file + f'.{lang_code}.srt'

    print(f"Connecting to LM Studio at {args.api_url}...")
    client = OpenAI(base_url=args.api_url, api_key=args.api_key)

    try:
        client.models.list()
    except Exception as e:
        print(f"Error: Could not connect to LM Studio at {args.api_url}. Is it running? Details: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading subtitles from {input_file}...")
    try:
        subs = pysrt.open(input_file)
    except Exception as e:
        print(f"Error parsing SRT file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(subs)} subtitles. Starting translation to {target_language}...")

    for i, sub in enumerate(subs):
        original_text = sub.text
        if not original_text.strip():
            continue
            
        translated_text = translate_text(client, original_text, target_language, args.model)
        sub.text = translated_text
        
        # Simple progress indicator
        print(f"[{i+1}/{len(subs)}] Translated", end='\r')

    print(f"\nSaving translations to {output_file}...")
    subs.save(output_file, encoding='utf-8')
    print("Done!")

if __name__ == "__main__":
    main()
