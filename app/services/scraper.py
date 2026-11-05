import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from app.core.config import BASE_URL, HEADERS

def fetch_deal(node_id: int):
    url = f"{BASE_URL}/node/{node_id}"
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    response = session.get(url)
    if response.status_code != 200:
        return None, response.status_code
    
    output_request(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')

    
    title_tag = soup.find('h1', id='title')
    title = title_tag.text.strip() if title_tag else "N/A"
    
    content_div = soup.find('div', class_='content')
    description = content_div.get_text(separator=" ", strip=True) if content_div else ""
    
    vote_up_tag = soup.find('span', class_='voteup')
    vote_down_tag = soup.find('span', class_='votedown')
    vote_up = vote_up_tag.text.strip() if vote_up_tag else "0"
    vote_down = vote_down_tag.text.strip() if vote_down_tag else "0"
    
    comments = []

    root_uls = soup.find_all('ul', class_='comment level0')

    for root_ul in root_uls:
        comments.extend(parse_comments_recursive(root_ul))

    # TODO: Get Date
    return {
        "node_id": node_id,
        "url": url,
        "title": title,
        "upvotes": vote_up,
        "downvotes": vote_down,
        "description": description,
        "comments_count": len(comments),
        "comments": comments
    }, 200

def parse_comments_recursive(ul_node):
    results = []
    # Use find_children to only process direct children of the current <ul>
    for li in ul_node.find_all('li', recursive=False):
        
        wrap = li.find('div', class_='comment-wrap')
        if not wrap:
            continue
        
        author_tag = wrap.find('div', class_='submitted').find('strong').find('a')
        author = author_tag.text.strip() if author_tag else "Anonymous"
        
        body_tag = wrap.find('div', class_='content')
        body = body_tag.get_text(separator=" ", strip=True) if body_tag else ""
        
        nested_ul = li.find('ul', class_='comment')
        children = []
        if nested_ul:
            children = parse_comments_recursive(nested_ul)
            
        results.append({
            "author": author,
            "comment": body,
            "children": children
        })
    return results


# TODO: New Deals

# TODO: Search Deal

def output_request(response):
    # Export response to text file
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"response_{date_str}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(response)