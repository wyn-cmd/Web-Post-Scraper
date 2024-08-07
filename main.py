# Version 1.0

import io
import os
import requests
import urllib.request
import PIL.Image as Image
from bs4 import BeautifulSoup



# function to dither the images of the post into 
def image_to_ascii(image_data, chars=" .:-=+*#%@"):


    img = Image.open(io.BytesIO(image_data))

    # convert image to greyscale
    img = img.convert('L')

    width, height = img.size
    aspect_ratio = height / width
    
    # adjust size
    new_width = 20
    new_height = int(new_width * aspect_ratio)
    img = img.resize((new_width, new_height))

    # get pixel data
    pixels = img.getdata()
    char_list = []

    # start going through each pixel and put a corresponding character into the list for each pixel
    for i in range(new_height):

        for j in range(new_width):

            pixel = pixels[i * new_width + j]
            char = chars[int(pixel / 256 * len(chars))]
            
            char_list.append(char)
    
    char_list.append('\n')

    text_image = ''.join(char_list)

    return text_image



# scrapes posts from eurus.servehttp.com and get information about them
def scrape_posts(url):

    response = requests.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')

    posts = []


    for post in soup.find_all('div', class_='card'):

        # find title

        title = post.find('a', class_='card-title').text.strip().replace('\n', '')  

        # get small description of post
        description = post.find('p', class_='card-text').text.strip()

        image = post.find('img')

        if image:
            image_url = 'https://eurus.servehttp.com' + image['src']


            if True:
                image_data = requests.get(image_url).content
                image_data = image_to_ascii(image_data)
                posts.append({'title': title, 'description': description, 'image_path': image_data})
            #except Exception as e:
            #    print(f"Error downloading image: {e}")
            #    posts.append({'title': title, 'description': description, 'image_path': None})
        else:
            posts.append({'title': title, 'description': description, 'image_path': None})


    return posts

# website
url = 'https://eurus.servehttp.com/posts/'

# scrape the posts
scraped_posts = scrape_posts(url)


# display them
if scraped_posts:
    print("---------------Scraped Posts---------------")

    for i in range(len(scraped_posts)):

        print(f"\n\n-------------------------------------------\nTitle: {scraped_posts[i]['title']}")
        print(f"\nDescription: \n{scraped_posts[i]['description']}")

        # display post image in dithered text
        if scraped_posts[i]['image_path']:
            n = 0
            for line in scraped_posts[i]['image_path']:
                if n < 20:
                    end = ''
                else:
                    end = '\n'
                    n = 0

                print(f"{line}", end=end)

                n += 1

        else:

            print("No image found")
        print("-------------------------------------------\n")
else:
    print("No posts found."
