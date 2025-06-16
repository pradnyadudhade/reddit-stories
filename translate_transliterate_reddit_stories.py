import json
import logging
from googletrans import Translator
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
from retrying import retry

# Setup logging
logging.basicConfig(filename='translate_transliterate.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize translator
translator = Translator()

# Configuration
INPUT_FILE = 'reddit_stories.json'
OUTPUT_FILE = 'reddit_stories_hindi_romanized.json'

@retry(stop_max_attempt_number=3, wait_fixed=2000)
def translate_to_hindi(text):
    """Translate text to Hindi with retries."""
    try:
        if not text or not isinstance(text, str):
            return text
        translated = translator.translate(text, dest='hi')
        return translated.text
    except Exception as e:
        logging.error(f"Translation error for text '{text[:50]}...': {e}")
        return text  # Return original text on failure

def transliterate_to_roman(text):
    """Transliterate Hindi (Devanagari) to Romanized Hindi (ITRANS)."""
    try:
        if not text or not isinstance(text, str):
            return text
        romanized = transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)
        return romanized
    except Exception as e:
        logging.error(f"Transliteration error for text '{text[:50]}...': {e}")
        return text  # Return original text on failure

def process_stories():
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

    # Process each story
    processed_stories = []
    for story in stories:
        try:
            logging.info(f"Processing story ID: {story.get('id')}")
            processed_story = story.copy()  # Preserve original fields
            # Translate to Hindi
            title_hindi = translate_to_hindi(story.get('title', ''))
            text_hindi = translate_to_hindi(story.get('text', ''))
            # Transliterate to Romanized Hindi
            processed_story['title_hindi_roman'] = transliterate_to_roman(title_hindi)
            processed_story['text_hindi_roman'] = transliterate_to_roman(text_hindi)
            processed_stories.append(processed_story)
        except Exception as e:
            logging.error(f"Error processing story ID {story.get('id')}: {e}")
            continue

    if not processed_stories:
        logging.warning("No stories processed successfully")
        print("No stories processed. Check translate_transliterate.log for details.")
        return []

    # Save to JSON
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(processed_stories, f, ensure_ascii=False, indent=2)
        logging.info(f"Saved {len(processed_stories)} processed stories to {OUTPUT_FILE}")
    except Exception as e:
        logging.error(f"Error saving to {OUTPUT_FILE}: {e}")
        print(f"Error saving processed stories: {e}")
        return processed_stories

    return processed_stories

def main():
    try:
        stories = process_stories()
        if stories:
            print(f"Processed {len(stories)} stories to Romanized Hindi:")
            for i, story in enumerate(stories, 1):
                print(f"\nStory {i}:")
                print(f"Subreddit: {story.get('subreddit')}")
                print(f"Original Title: {story.get('title')}")
                print(f"Romanized Hindi Title: {story.get('title_hindi_roman')}")
                print(f"Romanized Hindi Text: {story.get('text_hindi_roman')[:200]}...")  # Preview
                print(f"Score: {story.get('score')}, Comments: {story.get('comments')}")
        else:
            print("No stories processed. Check translate_transliterate.log for details.")
    except Exception as e:
        logging.error(f"Main error: {e}")
        print(f"Error occurred: {e}. Check translate_transliterate.log for details.")

if __name__ == "__main__":
    main()