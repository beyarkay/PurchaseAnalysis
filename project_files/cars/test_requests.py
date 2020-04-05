
import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options


url = "https://www.cars.co.za/usedcars/Western-Cape/"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
while True:
    request = ""
    while not request:
        try:
            request = requests.get(url, headers=headers)
            print(request.statuscode)
            break
        except:
            print("z")
            time.sleep(5)
            continue
    
    page = BeautifulSoup(request.text, features="html.parser")

    # Print out how many pages there are
    if len(item_links) == 0:
        pbar = tqdm(total=get_total_pages(page), disable=quiet)
    pbar.update(1)
    pbar.set_description(url)
    # Store all the links to cars from the current page
    item_links.update(get_links_on_page(page))

    # Find the link to the next page
    next_page_link = get_next_page_link(page)
    if next_page_link and (
            (limit is None) or len(item_links) <= limit):  # Check to see if we're at the last page or not
        url = next_page_link
    else:
        pbar.close()
        return list(item_links)
