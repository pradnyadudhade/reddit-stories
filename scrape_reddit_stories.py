import praw
import json
import logging
from datetime import datetime

# Setup logging to track progress and errors
logging.basicConfig(filename='reddit_scrape.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Reddit API setup (update with your credentials)
reddit = praw.Reddit(
    client_id="",  # Your client_id
    client_secret="",  # Your client_secret
    user_agent=""  # Your user_agent
)

# Configuration
SUBREDDITS = ['relationships', 'AmItheAsshole', 'relationship_advice', 'confessions', 'tifu']
KEYWORDS = ['drama', 'betrayal', 'cheating', 'breakup', 'affair', 'divorce']
OUTPUT_FILE = 'reddit_stories.json'

def scrape_reddit_stories():
    stories = []
    used_post_ids = set()

    for subreddit in SUBREDDITS:
        try:
            logging.info(f"Scraping subreddit: {subreddit}")
            for post in reddit.subreddit(subreddit).hot(limit=50):
                # Check if post is relevant and not already used
                if (post.id not in used_post_ids and
                    any(keyword.lower() in (post.title.lower() + ' ' + (post.selftext or '').lower())
                        for keyword in KEYWORDS)):
                    story_text = post.selftext or post.title
                    if len(story_text) > 100:  # Ensure enough content
                        stories.append({
                            'id': post.id,
                            'subreddit': subreddit,
                            'title': post.title,
                            'text': story_text[:1000],  # Limit to 1000 chars
                            'score': post.score,
                            'comments': len(post.comments),
                            'timestamp': datetime.utcfromtimestamp(post.created_utc).isoformat()
                        })
                        used_post_ids.add(post.id)
        except Exception as e:
            logging.error(f"Error scraping {subreddit}: {e}")
            continue

    # Sort by engagement (score + 2 * comments)
    stories = sorted(stories, key=lambda x: x['score'] + 2 * x['comments'], reverse=True)
    
    # Select top 10
    top_stories = stories[:10]
    
    if not top_stories:
        logging.warning("No stories found matching criteria")
        return []

    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(top_stories, f, ensure_ascii=False, indent=2)
    
    logging.info(f"Saved {len(top_stories)} stories to {OUTPUT_FILE}")
    return top_stories

def main():
    try:
        stories = scrape_reddit_stories()
        if stories:
            print(f"Scraped {len(stories)} stories:")
            for i, story in enumerate(stories, 1):
                print(f"\nStory {i}:")
                print(f"Subreddit: {story['subreddit']}")
                print(f"Title: {story['title']}")
                print(f"Text: {story['text'][:200]}...")  # Preview
                print(f"Score: {story['score']}, Comments: {story['comments']}")
        else:
            print("No stories found. Check logs for details.")
    except Exception as e:
        logging.error(f"Main error: {e}")
        print(f"Error occurred: {e}. Check reddit_scrape.log for details.")

if __name__ == "__main__":
    main()