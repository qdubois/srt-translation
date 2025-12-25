# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
#     "pysrt",
#     "google-generativeai",
# ]
# ///

import argparse
import sys
import os
import shutil
import subprocess
import re
from openai import OpenAI
import pysrt
import google.generativeai as genai

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

def translate_text(client, text, target_language="French", model="local-model", debug=False, provider="lm-studio"):
    """
    Translates text from English to the target language.
    """
    try:
        if provider == "gemini":
            # client is actually a genai.GenerativeModel instance
            prompt = f"You are a professional subtitle translator. Translate the following English subtitle text to {target_language}. Maintain the tone and context. Return ONLY the translated text, no explanations or quotes.\n\nText: {text}"
            response = client.generate_content(prompt)
            translated = response.text.strip()
        else:
            # client is an OpenAI instance
            messages = [
                {"role": "system", "content": f"/no_think You are a professional subtitle translator. Translate the following English subtitle text to {target_language}. Maintain the tone and context. Return ONLY the translated text, no explanations or quotes."},
                {"role": "user", "content": text}
            ]
            
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": 0.3,
            }
            
            # Only add extra_body for LM Studio if it's likely to support it
            if provider == "lm-studio":
                kwargs["extra_body"] = {"reasoning": {"effort": "low"}}
                
            response = client.chat.completions.create(**kwargs)
            translated = response.choices[0].message.content.strip()
            
            # Remove <think> blocks from reasoning models
            translated = re.sub(r'<think>.*?</think>', '', translated, flags=re.DOTALL).strip()

        if debug:
            print(f"\n[DEBUG] Original: {text}")
            print(f"[DEBUG] Translated: {translated}")
        return translated
    except Exception as e:
        print(f"Error translating line '{text}': {e}", file=sys.stderr)
        return text  # Return original text on failure

def main():
    parser = argparse.ArgumentParser(description="Translate SRT or MKV file from English to a target language using LM Studio or Gemini.")
    parser.add_argument("input_file", help="Path to the input file (e.g., movie.srt or movie.mkv).")

    parser.add_argument("--provider", choices=["lm-studio", "gemini"], default="lm-studio", help="API provider (default: lm-studio)")
    parser.add_argument("--api-url", help="API URL (default for LM Studio: http://localhost:1234/v1)")
    parser.add_argument("--api-key", help="API Key (default for LM Studio: lm-studio, for Gemini: uses GEMINI_API_KEY env var if not provided)")
    parser.add_argument("--model", help="Model identifier (default for LM Studio: qwen/qwen3-8b, for Gemini: gemini-flash-lite-latest)")
    parser.add_argument("--target-language", "-l", help="Target language for translation (default: prompts user)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output to print original and translated text")

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # Language prompt
    target_language = args.target_language
    if not target_language:
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

    # Initialize client based on provider
    if args.provider == "gemini":
        api_key = args.api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("Error: Gemini API key is required. Use --api-key or set GEMINI_API_KEY environment variable.", file=sys.stderr)
            sys.exit(1)
        model_name = args.model or "gemini-flash-lite-latest"
        
        print(f"Connecting to Gemini using model {model_name}...")
        genai.configure(api_key=api_key)
        client = genai.GenerativeModel(model_name)
    else:
        api_url = args.api_url or "http://localhost:1234/v1"
        api_key = args.api_key or "lm-studio"
        model_name = args.model or "qwen/qwen3-8b"
        
        print(f"Connecting to LM Studio at {api_url}...")
        client = OpenAI(base_url=api_url, api_key=api_key)

        try:
            client.models.list()
        except Exception as e:
            print(f"Error: Could not connect to LM Studio at {api_url}. Is it running? Details: {e}", file=sys.stderr)
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
            
        translated_text = translate_text(client, original_text, target_language, model_name, args.debug, args.provider)
        sub.text = translated_text
        
        # Simple progress indicator
        if not args.debug:
            print(f"[{i+1}/{len(subs)}] Translated", end='\r')

    print(f"\nSaving translations to {output_file}...")
    subs.save(output_file, encoding='utf-8')
    print("Done!")

if __name__ == "__main__":
    main()
