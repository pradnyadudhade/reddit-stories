import json
import logging
import os
from gtts import gTTS

# Setup logging
logging.basicConfig(filename='audio_generation.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
INPUT_FILE = 'reddit_stories_hindi_romanized.json'
OUTPUT_DIR = 'audio_files'

def generate_audio(text, output_file, lang='hi'):
    """Generate audio from text using gTTS."""
    try:
        if not text or not isinstance(text, str):
            raise ValueError("Invalid or empty text")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(output_file)
        if os.path.getsize(output_file) == 0:
            raise ValueError("Generated audio file is empty")
        return output_file
    except Exception as e:
        logging.error(f"Audio generation error for text '{text[:50]}...': {e}")
        raise

def process_stories():
    # Create output directory
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Read JSON file
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            stories = json.load(f)
    except FileNotFoundError:
        logging.error(f"Input file {INPUT_FILE} not found")
        print(f"Error: {INPUT_FILE} not found. Please ensure the file exists.")
        return []
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in {INPUT_FILE}")
        print(f"Error: Invalid JSON format in {INPUT_FILE}.")
        return []

    if not stories:
        logging.warning("No stories found in input file")
        print("No stories to process.")
        return []

    # Generate audio for each story
    audio_files = []
    for i, story in enumerate(stories, 1):
        try:
            logging.info(f"Processing story ID: {story.get('id')}")
            text = story.get('text_hindi_roman', '')
            if not text:
                logging.warning(f"No Romanized Hindi text for story ID {story.get('id')}")
                continue
            output_file = os.path.join(OUTPUT_DIR, f"story_{i}.mp3")
            generate_audio(text, output_file)
            audio_files.append({
                'id': story.get('id'),
                'subreddit': story.get('subreddit'),
                'title': story.get('title'),
                'text_hindi_roman': text,
                'audio_file': output_file
            })
            logging.info(f"Generated audio: {output_file}")
        except Exception as e:
            logging.error(f"Error processing story ID {story.get('id')}: {e}")
            continue

    if not audio_files:
        logging.warning("No audio files generated successfully")
        print("No audio files generated. Check audio_generation.log for details.")
        return []

    return audio_files

def main():
    try:
        audio_files = process_stories()
        if audio_files:
            print(f"Generated {len(audio_files)} audio files:")
            for i, audio in enumerate(audio_files, 1):
                print(f"\nAudio {i}:")
                print(f"Subreddit: {audio.get('subreddit')}")
                print(f"Original Title: {audio.get('title')}")
                print(f"Romanized Hindi Text: {audio.get('text_hindi_roman')[:200]}...")  # Preview
                print(f"Audio File: {audio.get('audio_file')}")
        else:
            print("No audio files generated. Check audio_generation.log for details.")
    except Exception as e:
        logging.error(f"Main error: {e}")
        print(f"Error occurred: {e}. Check audio_generation.log for details.")

if __name__ == "__main__":
    main()