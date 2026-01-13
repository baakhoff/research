import requests
import pandas as pd
import json
from dotenv import load_dotenv
import os
import xml.etree.ElementTree as ET
load_dotenv()

def check_page_exists(page):
    """Checks if a page exists for a given ID using the Rule34 API."""
    credentials = os.getenv('R34_ACCESS_CREDENTIALS')
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=tag&q=index&pid={page}&limit=1000"
    try:
        response = requests.get(f"{url}{credentials}", timeout=10)
        root = ET.fromstring(response.content)
        return len(root.findall('tag')) > 0
    except Exception:
        return False


def find_total_tag_pages(low=1000, high=3000):
    """Performs a binary search to find the highest valid tag ID."""
    result = low
    while low <= high:
        mid = (low + high) // 2
        print(f"Probing ID: {mid}...", end="\r")
        if check_page_exists(mid):
            result = mid
            low = mid + 1
        else:
            high = mid - 1
    return result

total_tag_pages = find_total_tag_pages()
print(f"\nApproximate total tags (highest ID): {total_tag_pages}")

df = pd.DataFrame()
credentials = os.getenv('R34_ACCESS_CREDENTIALS')
for i in range(total_tag_pages+1):
    try:
        if i in pd.read_csv('../data/r34data/rule34_tags.csv', usecols=['page'])['page'].values:
            print('skipped',i)
            continue
    except:
        pass
    url = f"https://api.rule34.xxx/index.php?page=dapi&s=tag&q=index&pid={i}&limit=1000"
    response = requests.get(f"{url}{credentials}", timeout=100)
    df = pd.read_xml(response.text)
    df['page'] = i
    if i == 0:
        df.to_csv('../data/r34data/rule34_tags.csv', mode='w', index=False, header=True)
    else:
        df.to_csv('../data/r34data/rule34_tags.csv', mode='a', index=False, header=False)

