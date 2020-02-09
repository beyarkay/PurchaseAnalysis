#!/usr/bin/python -u
# TODO refactor the get_website_links so that you don't have duplicates in scrape_XXX.py
import datetime
import sys
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from tqdm import tqdm

DEBUG = False
NOW = datetime.datetime.now().strftime('%Y-%m-%d')
engine = create_engine('postgresql+psycopg2://pi:liberdade@192.168.1.38/items', echo=False)


def main():
    if len(sys.argv) == 3:
        quiet = True if int(sys.argv[1]) else False
        limit = int(sys.argv[2]) if sys.argv[2].isnumeric() else -1
        property24_links = get_property24_links(quiet=quiet, limit=limit)
    else:
        property24_links = get_property24_links()
    populate_db_from_property24(property24_links)


def get_website_links(url, get_total_pages, get_links_on_page, get_next_page_link, quiet, limit):
    """
    Go through every link at this URL (and subsequently every page given by get_next_page_link)
    Log the id, date, price combo in the DB
    If the id, price combo isn't in the DB at all, add the link to returner[]
    returner gets passed on to be parsed in detail

    Parameters
    ----------
    url: string
    get_total_pages: function(): int: Used once on the first page, returns the total number of pages to traverse
    get_links_on_page: function(page): Returns a list of full links for every relevant item on that page
    get_next_page_link: function(page): Returns a full link to the next page if it exists, None otherwise

    Returns
    -------
    A list of the all the full item links
    """
    global pbar
    item_links = set()
    print(f"Fetching {'all' if limit > 0 else str(limit)} links from {url}")
    while True:
        request = ""
        while not request:
            try:
                request = requests.get(url)
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
                (not limit) or len(item_links) <= limit):  # Check to see if we're at the last page or not
            url = next_page_link
        else:
            pbar.close()
            return list(item_links)


def get_property24_links(quiet=True, limit=-1):
    if True:
        url = "https://www.property24.com/for-sale/cape-town/western-cape/432"
    else:
        url = "https://www.property24.com/to-rent/cape-town/western-cape/432"
    domain = "https://www.property24.com"

    def get_total_pages(page):
        return int(page.find("ul", "pagination").find_all("li")[-1].find("a").get("data-pagenumber"))

    def get_links_on_page(page):
        links = [domain + div.find("a").get("href") for div in page.select("div.p24_regularTile.js_rollover_container")]
        # links = [domain + link.get("href") for link in page.find_all("a", class_="vehicle-list__vehicle-name")]

        prices = [re.sub(r"\D", "", link.text) for link in page.find_all("div", class_="p24_price")]
        returner = set()
        for link, price in zip(links, prices):
            # TODO adjust this to execute in batches, instead of all together
            result = engine.execute(f"""
                    SELECT COUNT(*)
                    FROM dates_cars
                    WHERE website='{domain}' AND website_id='{link.split("/")[-2]}';
                """).fetchall()

            if result[0][0] == 0:
                returner.add(link)
            engine.execute(f"""
                INSERT INTO dates_cars (date, website, website_id, price) 
                VALUES ('{NOW}', '{domain}', '{link.split("/")[-2]}', {price});
                """)

        return returner

    def get_next_page_link(page):
        next_page_links = page.find("div", "p24_pager").find("a", "pull-right")
        if 'text-muted' not in next_page_links.get("class"):
            return next_page_links.get("href")
        else:
            return None

    return get_website_links(url, domain, get_total_pages, get_links_on_page, get_next_page_link, quiet, limit)


def populate_db_from_property24(property24_links, quiet=False, limit=-1):
    """
    Add the full details from every link in carscoza_links
    carscoza_links is assumed to have only unique items

    Parameters
    ----------
    carscoza_links
    quiet
    limit

    Returns
    -------

    """

    # Ensure the DB is setup with a dates_cars table
    if not engine.dialect.has_table(engine, "dates_cars"):
        engine.execute("""
                    create table dates_cars
                    (
                        date       TEXT,
                        website    TEXT,
                        website_id TEXT,
                        price      FLOAT
                    );
                    """)
    # Initialise some variables
    domain = "https://www.cars.co.za"
    if limit:
        property24_links = property24_links[:limit]
    car_dicts = []
    date_dicts = []
    print(f"Fetching data from {len(property24_links)} links")
    for i, link in enumerate(tqdm(property24_links)):
        page = ""
        while not page:
            try:
                page = requests.get(link)
                break
            except:
                print("z")
                time.sleep(5)
                continue

        soup = BeautifulSoup(page.text, features="html.parser")
        date = {
            "date": NOW,
            "website": "/".join(link.split(r"/")[:3]),
            "website_id": re.search("\(ID:(\d+)\)", soup.title.text).groups()[0],
            "price": float(re.sub(r"\D", "", soup.find("div", class_="price").text))
        }
        # predefine the dictionary because it's the easiest way to ensure the dataframe is in a decent order
        car = {
            "website_id": re.search("\(ID:(\d+)\)", soup.title.text).groups()[0],
            "website": "/".join(link.split(r"/")[:3]),
            "price":
                float(re.sub(r"\D", "", soup.find("div", class_="price").text)),
            "heading":
                re.sub("\s", " ", soup.find("h1", class_="heading").text.strip()),
            "link":
                link,
            "img_link":
                [link.get("src") for link in soup.find_all("img", class_="gallery__slider-image") if
                 link.has_attr("src")],
            "make":
                [link.text.split("\n \n") for link in soup.find_all("div", class_="js-breadcrumbs")][0][2].lower(),
            "model":
                [link.text.split("\n \n") for link in soup.find_all("div", class_="js-breadcrumbs")][0][3].lower(),
            "odometer_km": None,
            "year": None,
            "date_accessed": datetime.datetime.now().strftime('%Y-%m-%d'),
            "time_accessed": datetime.datetime.now().strftime('%H:%M:%S'),
            "colours": None,
            "area": None,
            "dealer": None,
            "dealer_location": None,
            "dealer_link": None,
            "engine_power_max_kW": None,
            "engine_size_l": None,
            "engine_fuel_type": None,
            "engine_fuel_tank_l": None,
            "engine_transmission": None,
            "performace_0_to_100_s": None,
            "performace_speed_max_kmph": None,
            "economy_fuel_consumption_lpkm": None,
            "economy_fuel_range_km": None,
            "economy_CO2_gpkm": None,
            "safety_ABS": None,
            "safety_EBD": None,
            "safety_brake_assist": None,
            "safety_driver_airbag": None,
            "safety_passenger_airbag": None,
            "safety_airbag_quantity": None,
            "features_bluetooth": None,
            "features_aircon": None,
            "specs_doors": None,
            "specs_seats": None,
            "specs_kerb_weight": None,
            "options": None,
            "description": None,
        }

        car_dicts.append(car)
        date_dicts.append(date)

    if len(car_dicts) > 0:
        cars = pd.DataFrame(car_dicts)
        dates = pd.DataFrame(date_dicts)
        if engine.dialect.has_table(engine, "cars"):
            db_cars = pd.read_sql_table("cars", con=engine)
            cars = pd.concat([db_cars, cars])
            cars.drop_duplicates(subset=['website_id', 'website'], inplace=True, keep='last')

        db_dates = pd.read_sql_table("dates_cars", con=engine)
        dates = pd.concat([db_dates, dates])
        dates.drop_duplicates(subset=['date', 'price', 'website_id', 'website'], inplace=True, keep='last')

        cars.to_sql('cars', con=engine, if_exists='replace', index=False)
        dates.to_sql('dates_cars', con=engine, if_exists='replace', index=False)
        print(f"DB updated with data from {domain} at {NOW}")
    else:
        print(f"len(car_dicts) == {len(car_dicts)}, not doing anything")


if __name__ == '__main__':
    main()
