# Version 1.2

import io
import requests
from bs4 import BeautifulSoup
from PIL import Image

BASE_URL = 'https://eurus.servehttp.com'
DEFAULT_CHARS = " .:-=+*#%@"


def image_to_ascii(image_data, chars=DEFAULT_CHARS, width=20):
    """Convert raw image bytes into a scaled ASCII art string."""
    with Image.open(io.BytesIO(image_data)) as img:
        img = img.convert('L')
        orig_width, orig_height = img.size
        aspect_ratio = orig_height / orig_width
        
        new_height = int(width * aspect_ratio)
        img = img.resize((width, new_height))

        pixels = list(img.getdata())
        
    char_list = []
    for i in range(new_height):
        for j in range(width):
            pixel = pixels[i * width + j]
            char_index = int(pixel / 256 * len(chars))
            char_list.append(chars[char_index])
        char_list.append('\n')

    return ''.join(char_list)


def fetch_image_ascii(image_url):
    """Safely download an image and return its ASCII representation."""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        return image_to_ascii(response.content)
    except requests.RequestException as e:
        print(f"Error downloading image {image_url}: {e}")
        return None


def scrape_posts(url):
    """Scrape posts including titles, descriptions, and ASCII-converted images from the target URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    posts = []

    for post in soup.find_all('div', class_='card'):
        title_elem = post.find('a', class_='card-title')
        desc_elem = post.find('p', class_='card-text')
        
        if not title_elem or not desc_elem:
            continue

        title = title_elem.text.strip().replace('\n', '')
        description = desc_elem.text.strip()
        
        image_ascii = None
        image_elem = post.find('img')
        
        if image_elem and image_elem.has_attr('src'):
            image_url = BASE_URL + image_elem['src']
            image_ascii = fetch_image_ascii(image_url)

        posts.append({
            'title': title, 
            'description': description, 
            'image_path': image_ascii
        })

    return posts


if __name__ == '__main__':
    target_url = 'https://eurus.servehttp.com/posts/'
    scraped_posts = scrape_posts(target_url)

    if scraped_posts:
        print("---------------Scraped Posts---------------")
        for post in scraped_posts:
            print(f"\n\n-------------------------------------------\nTitle: {post['title']}")
            print(f"\nDescription: \n{post['description']}")

            if post['image_path']:
                print(post['image_path'], end='')
            else:
                print("No image found")
            print("-------------------------------------------\n")
    else:
        print("No posts found.")