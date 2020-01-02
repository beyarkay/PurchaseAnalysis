#!/usr/bin/python -u
#TODO refactor the get_website_links so that you don't have duplicates in scrape_XXX.py
import datetime
import sys
import time
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from sqlalchemy import create_engine
from tqdm import tqdm
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

DEBUG = False
NOW = datetime.datetime.now().strftime('%Y-%m-%d')


def main():
    property24_links = get_property24_links(should_get_sales=True)
    property24_links.extend(get_property24_links(should_get_sales=False))
    print(property24_links[:5])
    print(len(property24_links))
    path = "project_files/property/property24_links.txt"
    with open(path, "w+") as write_file:
        write_file.write("\n".join(property24_links))

    # with open("project_files/property/property24_links.txt", "r") as property24_file:
    #     property24_links = [line.strip() for line in property24_file.readlines()]
    # populate_db_from_autotradercoza(property24_links[:10])


def get_website_links(url, domain, get_total_pages, get_links_on_page, get_next_page_link):
    """

    Parameters
    ----------
    url: string
    domain: string
    get_total_pages: function(): int: Used once on the first page, returns the total number of pages to traverse
    get_links_on_page: function(page): Returns a list of full links for every relevant item on that page
    get_next_page_link: function(page): Returns a full link to the next page if it exists, None otherwise

    Returns
    -------
    A list of the all the full item links
    """
    global pbar
    item_links = []
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
            pbar = tqdm(total=get_total_pages(page))
        pbar.update(1)
        pbar.set_description(url)
        # Store all the links to cars from the current page
        item_links.extend(get_links_on_page(page))

        # Find the link to the next page
        next_page_link = get_next_page_link(page)
        if next_page_link:  # Check to see if we're at the last page or not
            url = next_page_link
        else:
            return list(set(item_links))  # remove any duplicate links


def get_property24_links(should_get_sales):
    if should_get_sales:
        url = "https://www.property24.com/for-sale/cape-town/western-cape/432"
    else:
        url = "https://www.property24.com/to-rent/cape-town/western-cape/432"
    domain = "https://www.property24.com"

    def get_total_pages(page):
        return int(page.find("ul", "pagination").find_all("li")[-1].find("a").get("data-pagenumber"))

    def get_links_on_page(page):
        return [domain + div.find("a").get("href") for div in page.select("div.p24_regularTile.js_rollover_container")]

    def get_next_page_link(page):
        next_page_links = page.find("div", "p24_pager").find("a", "pull-right")
        if 'text-muted' not in next_page_links.get("class"):
            return next_page_links.get("href")
        else:
            return None

    return get_website_links(url, domain, get_total_pages, get_links_on_page, get_next_page_link)

def populate_db_from_property24(property24_links):
    engine = create_engine('sqlite:///project_files/cars/items.db', echo=False)
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
    domain = "https://www.cars.co.za"
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
        dealer_location = soup.select(".number-tracker__address")
        if dealer_location:
            car["dealer_location"] = dealer_location[0].text.strip()
        dealer = soup.select(".heading.heading_centered.number-tracker__name")
        if dealer:
            car["dealer"] = dealer[0].text.strip()
        elif soup.select(".vehicle-view__content-links.vehicle-view__content-links_blue"):
            car["dealer"] = soup.select(".vehicle-view__content-links.vehicle-view__content-links_blue")[
                0].text.strip()
        elif "private" in soup.select(".lead-form__title")[0].text.lower():
            car["dealer"] = "Private"

        dealer_link = soup.select(".vehicle-view__content-links.vehicle-view__content-links_blue")
        if dealer_link:
            car["dealer_link"] = domain + dealer_link[0].get("href")
        elif soup.select(".bbtn.btn-primary.button.button_size_small.button_side-pad_medium.stock-reel__view-btn"):
            car["dealer_link"] = domain + soup.select(
                ".bbtn.btn-primary.button.button_size_small.button_side-pad_medium.stock-reel__view-btn")[0].get(
                "href")
        car["img_link"] = car["img_link"][0] if len(car["img_link"]) > 0 else None

        keys = [link.text for link in soup.find_all("td", class_="vehicle-details__label")]
        values = [link.text for link in soup.find_all("td", class_="vehicle-details__value")]
        data_dict = {key: value for key, value in zip(keys, values)}

        # normalise the colours to be something workable
        colours = {
            "white": re.compile("(white)"),
            "grey": re.compile("(grey|gray|charcoal)"),
            "silver": re.compile("(silver)"),
            "black": re.compile("(black)"),
            "nan": re.compile("(nan)"),
            "blue": re.compile("(blue|sea)"),
            "orange": re.compile("(orange)"),
            "red": re.compile("(pepper|red)"),
        }
        actual_colours = []
        if data_dict.get("Colour"):
            item = data_dict.get("Colour").lower()
            for k, v in colours.items():
                if re.search(v, item):
                    actual_colours.append(k)
            if not actual_colours:
                actual_colours.append(item.replace(",", ""))
            car["colours"] = " ".join(actual_colours)

        car["odometer_km"] = re.sub(r"\D", "", data_dict.get("Mileage")) if data_dict.get("Mileage") else None
        car["odometer_km"] = float(car["odometer_km"]) if len(car["odometer_km"]) > 0 else None
        car["year"] = float(data_dict.get("Year")) if data_dict.get("Year") else None
        car["area"] = data_dict.get("Area").lower() if data_dict.get("Area") else None
        car["engine_transmission"] = data_dict.get("Transmission").strip()[0].lower() if data_dict.get(
            "Transmission") else None
        car["engine_fuel_type"] = data_dict.get("Fuel Type").strip()[0].lower() if data_dict.get(
            "Fuel Type") else None
        car["options"] = data_dict.get("Options") if data_dict.get("Options") else None

        car["description"] = \
            [link.text.strip() for link in soup.find_all("div", class_="vehicle-view__content")]
        car["description"] = car["description"][0] if len(car["description"]) > 0 else None
        # First extract the table from the webpage
        table_data = [[td.text for td in link.find_all("td")] for link in
                      soup.find_all("table", class_="vehicle-specs__table")]
        # Then put the key-value pairs together into tuples
        zipped_data = [list(zip(sub_list[0::2], sub_list[1::2])) for sub_list in table_data]
        # Then flatten the list of lists to be just one long list
        flat_list = [item for sublist in zipped_data for item in sublist]
        # finally, convert the list of tuples into a dict
        data_dict = dict(flat_list)
        # And now add the data into the car dict
        car["economy_fuel_consumption_lpkm"] = float(
            data_dict.get("Average").replace("l/100km", "").strip()) if data_dict.get("Average") else None
        car["engine_power_max_kW"] = float(
            data_dict.get("Power Max").replace("Kw", "").strip()) if data_dict.get("Power Max") else None
        car["engine_size_l"] = float(data_dict.get("Engine Size").replace("l", "").strip()) if data_dict.get(
            "Power Max") else None
        car["engine_fuel_tank_l"] = float(
            data_dict.get("Fuel tank capacity").replace("l", "").strip()) if data_dict.get(
            "Fuel tank capacity") else None
        car["performace_0_to_100_s"] = float(
            data_dict.get("0-100Kph").replace("s", "").strip()) if data_dict.get("0-100Kph") and data_dict.get(
            "0-100Kph").replace("s", "").strip().replace(".", "", 1).isdigit() else None
        car["performace_speed_max_kmph"] = float(
            data_dict.get("Top speed").replace("Km/h", "").strip()) if data_dict.get("Top speed") else None
        car["economy_fuel_range_km"] = float(
            data_dict.get("Fuel range").replace("Km", "").replace(" ", "").strip()) if data_dict.get(
            "Fuel range") else None
        car["economy_CO2_gpkm"] = float(data_dict.get("Co2").replace("g/km", "").strip()) if data_dict.get(
            "Co2") else None
        car["safety_ABS"] = True if data_dict.get("ABS") else False
        car["safety_EBD"] = True if data_dict.get("EBD") else False
        car["safety_brake_assist"] = True if data_dict.get("Brake assist") else False
        car["safety_driver_airbag"] = True if data_dict.get("Driver airbag") else False
        car["safety_passenger_airbag"] = True if data_dict.get("Passenger airbag") else False
        car["safety_airbag_quantity"] = float(data_dict.get("Airbag quantity").strip()[0]) if data_dict.get(
            "Airbag quantity") else None
        car["features_bluetooth"] = True if data_dict.get("Bluetooth connectivity") else False
        car["features_aircon"] = True if data_dict.get("Air conditioning") else False
        car["specs_doors"] = float(data_dict.get("Doors").strip()) if data_dict.get("Doors") else None
        car["specs_seats"] = float(data_dict.get("Seats quantity").replace("l", "").strip()) if data_dict.get(
            "Seats quantity") else None
        car["specs_kerb_weight"] = float(
            data_dict.get("Kerb weight").replace("Kg", "").split("-")[0].strip()) if data_dict.get(
            "Kerb weight") else None
        car["specs_central_locking"] = data_dict.get("Central locking").strip().lower() if data_dict.get(
            "Central locking") else None
        car_dicts.append(car)
        date_dicts.append(date)
    print(" done, processing db")

    cars = pd.DataFrame(car_dicts)
    dates = pd.DataFrame(date_dicts)
    if engine.dialect.has_table(engine, "cars"):
        db_cars = pd.read_sql_table("cars", con=engine)
        cars = pd.concat([db_cars, cars])
        cars.drop_duplicates(subset=['website_id', 'website'], inplace=True, keep='last')

    db_dates = pd.read_sql_table("dates_cars", con=engine)
    dates = pd.concat([db_dates, dates])
    dates.drop_duplicates(subset=['date', 'price', 'website_id', 'website'], inplace=True, keep='last')

    # cars.to_sql('cars', con=engine, if_exists='replace', index=False)
    # dates.to_sql('dates_cars', con=engine, if_exists='replace', index=False)
    print(f"DB updated with data from {domain} at {NOW}")


if __name__ == '__main__':
    main()
