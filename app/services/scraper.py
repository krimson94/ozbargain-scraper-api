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
    ozbdeal = soup.find('div', class_='node-ozbdeal')
    
    description_tag = soup.find('div', class_='content')
    description = description_tag.get_text(separator=" ", strip=True) if description_tag else ""
    
    vote_up_tag = ozbdeal.find('span', class_='voteup')
    vote_down_tag = ozbdeal.find('span', class_='votedown')
    vote_up = vote_up_tag.text.strip() if vote_up_tag else "0"
    vote_down = vote_down_tag.text.strip() if vote_down_tag else "0"
    
    submitted_tag = ozbdeal.find('div', class_='submitted')
    date_time = get_date(submitted_tag)
    comments = []
    
    root_uls = soup.find_all('ul', class_='comment level0')
    
    for root_ul in root_uls:
        comments.extend(parse_comments_recursive(root_ul))
    total_comments = count_total_comments(comments)
    
    return {
        "node_id": node_id,
        "url": url,
        "title": title,
        "upvotes": vote_up,
        "downvotes": vote_down,
        "description": description,
        "date_submitted": date_time,
        "comments_count": total_comments,
        "comments": comments
    }, 200

def parse_comments_recursive(ul_node):
    results = []
    for li in ul_node.find_all('li', recursive=False):
        
        wrap = li.find('div', class_='comment-wrap')
        if not wrap:
            continue
        
        author_tag = wrap.find('div', class_='submitted').find('strong').find('a')
        author = author_tag.text.strip() if author_tag else "Anonymous"
        
        body_tag = wrap.find('div', class_='content')
        body = body_tag.get_text(separator=" ", strip=True) if body_tag else ""
        submitted_tag = wrap.find('div', class_='submitted')
        date_time = get_date(submitted_tag)
        nested_ul = li.find('ul', class_='comment')
        children = []
        if nested_ul:
            children = parse_comments_recursive(nested_ul)
            
        results.append({
            "author": author,
            "comment": body,
            "date_submitted": date_time,
            "children": children
        })
    return results

def count_total_comments(comment_list):
    count = 0
    for comment in comment_list:
        count += 1  # Count the comment itself
        count += count_total_comments(comment.get("children", [])) # Count its children
    return count

# TODO: New Deals
def fetch_new_deals():
    url = f"{BASE_URL}/deals"
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    response = session.get(url)
    if response.status_code != 200:
        return None, response.status_code
    
    soup = BeautifulSoup(response.text, 'html.parser')
    deals = []
    
    output_request(response.text)
    
    for node in soup.select('div.node'):
        title_tag = node.find('h2', class_='title')
        title = title_tag.text.strip() if title_tag else "N/A"
        link = title_tag.find('a').get('href') if title_tag else ""
        if link.startswith("/"):
            link = f"{BASE_URL}" + link
        description_tag = node.find('div', class_='content')
        description =  description_tag.text.strip() if description_tag else ""
        
        comments_count = "0"
        tags = []
        expiry_date = "N/A"
        
        submitted_tag = node.find('div', class_='submitted')
        date_time = get_date(submitted_tag)
    
        img_tag = node.find('div', class_='foxshot-container').find('img').get('src')
        img_url = img_tag if img_tag else ""
        if img_url.startswith("/"):
            img_url = f"{BASE_URL}" + img_url
            
        deals.append({
            "title": title,
            "link": link,
            "description": description,
            "date_submitted": date_time,
            "image_url": img_url
        })
        
    return deals, 200

# TODO: Search Deal

def output_request(response: str):
    # Export response to text file
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"response_{date_str}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(response)

def get_date(submitted_tag):
    submitted = submitted_tag.text.strip() if submitted_tag else ""
    # Relaxed regex to allow for different separators or extra spaces
    date_time_match = re.search(r'(\d{2}/\d{2}/\d{4})\s*[-]?\s*(\d{2}:\d{2})', submitted)
    
    if date_time_match:
        date_part = date_time_match.group(1)
        time_part = date_time_match.group(2)
        try:
            return datetime.strptime(f"{date_part} {time_part}", "%d/%m/%Y %H:%M")
        except ValueError:
            pass
            
    return datetime(1970, 1, 1)  # Default fallback
