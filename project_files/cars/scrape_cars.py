#!/usr/bin/python -u
import datetime
import sys
import time
import re
import time
from random import random

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
    carscoza_links = get_cars_links()
    # autotrader_links = get_autotrader_links()
    # print(len(autotrader_links))
    # with open("project_files/cars/cars_links.txt", "r") as cars_file:
    #     carscoza_links = [line.strip() for line in cars_file.readlines()]
    # with open("project_files/cars/autotrader_links.txt", "w+") as cars_file:
    #     cars_file.writelines("\n".join(autotrader_links))
    #     # autotrader_links = [line.strip() for line in cars_file.readlines()]
    populate_db_from_carscoza(carscoza_links)
    # populate_db_from_autotradercoza(autotrader_links[:10])
    with open("log.txt", "a") as write_file:
        write_file.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},carscoza: {len(carscoza_links)}\n")



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


def get_cars_links():
    url = "https://www.cars.co.za/searchVehicle.php?new_or_used=Used&make_model=&vfs_area=Western+Cape&agent_locality=&price_range=50000+-+74999%7C75000+-+99999%7C100000+-+124999%7C125000+-+149999&os=&locality=&body_type_exact=Hatchback&transmission=&fuel_type=&login_type=&mapped_colour=black%7Cgrey%7Csilver&vfs_year=&vfs_mileage=&vehicle_axle_config=&keyword=&sort=vfs_price&P=1"
    domain = "https://www.cars.co.za"

    def get_total_pages(page):
        items = \
            [div.get_text() for div in
             page.select('div.resultsnum.pagination__page-number.pagination__page-number_right')][
                0].split('\n')
        total_pages = int(int(items[-1].strip()) / 20 + 1)
        return total_pages

    def get_links_on_page(page):
        return [domain + link.get("href") for link in page.find_all("a", class_="vehicle-list__vehicle-name")]

    def get_next_page_link(page):
        next_page_links = page.select(".pagination__nav.fa-right-open-big")
        if next_page_links:
            return domain + next_page_links[0].get("href")
        else:
            return None

    return get_website_links(url, domain, get_total_pages, get_links_on_page, get_next_page_link)


def get_autotrader_links():
    url = "https://www.autotrader.co.za/cars-for-sale/western-cape/p-9?price=50001-to-200000&bodytype=hatchback&bodytype=sedan&colour=Black&colour=Grey&colour=Silver&colour=White&isused=True"
    domain = "https://www.autotrader.co.za"

    def get_total_pages(page):
        return int([li.a for li in page.find_all('li', 'e-page-number')][-1].get_text())

    def get_links_on_page(page):
        item_links = [domain + link.find("a").get("href") for link in
                      page.find_all("div", ["e-available", "m-has-photos"])]
        item_links.extend([domain + link.get("href") for link in page.select("a.b-featured-result-tile")])
        return item_links

    def get_next_page_link(page):
        next_page_links = page.select("a.gm-float-right.e-pagination-link")
        if next_page_links and next_page_links[0].has_attr("href"):
            min_sleep = 5   # autotrader has bot-protection, so sleep for a random amount between page loads
            max_sleep = 9
            time.sleep(round(random() * max_sleep + min_sleep, 2))
            return domain + next_page_links[0].get("href")
        else:
            return None

    return get_website_links(url, domain, get_total_pages, get_links_on_page, get_next_page_link)


def process_autotrader_page(autotrader_link):
    options = Options()
    options.headless = True
    driver = Chrome(options=options)
    driver.get(autotrader_link)
    for link in driver.find_elements_by_css_selector('div.b-accordion.m-specification-accordion'):
        link.click()
    # element = driver.find_element_by_css_selector(".e-read-more")
    # if element:
    #     element.click()
    html = driver.page_source
    driver.close()
    return html


def populate_db_from_carscoza(carscoza_links):
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
    print(f"Fetching data from {len(carscoza_links)} links")
    for i, link in enumerate(tqdm(carscoza_links)):
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


def populate_db_from_autotradercoza(autotrader_links):
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
    domain = "https://www.autotrader.co.za"
    car_dicts = []
    date_dicts = []
    print(f"Fetching data from {len(autotrader_links)} links")
    pbar = tqdm(autotrader_links)
    for i, link in enumerate(pbar):
        pbar.set_description(link)
        html = ""
        while not html:
            try:
                html = process_autotrader_page(link)
                break
            except Exception as e:
                print("error: " + e)
                time.sleep(5)
                continue

        soup = BeautifulSoup(html, features="html.parser")
        if soup.body.text == "The service is unavailable.":
            pbar.close()
            print(f"ERROR: Autotrader is unavailable, saving {len(car_dicts)} cars to DB")
            break
        date = {
            "date": NOW,
            "website": "/".join(link.split(r"/")[:3]),
            "website_id": re.search(r"ID: (\d+)", soup.title.text).groups()[0],
            "price": float(re.sub(r"\D", "", soup.find("div", class_="e-price").text))
        }
        # predefine the dictionary because it's the easiest way to ensure the dataframe is in a decent order
        car = {
            "website_id": date["website_id"],
            "website": date["website"],
            "price": date["price"],
            "heading":
                soup.find("h1", class_="e-listing-title").text.strip(),
            "link":
                link,
            "img_link":
                [re.sub("/Crop.+", "", link.get("src")) for link in soup.select("img.e-gallery-image") if
                 link.has_attr("src")],
            "make":
                [link.get_text() for link in soup.find_all("span", itemprop="name")][3].lower(),
            "model":
                [link.get_text() for link in soup.find_all("span", itemprop="name")][4].lower(),
            "odometer_km": float(re.sub(r"\D", "", soup.find("li", title="Mileage").get_text().strip())),
            "year": float(soup.find("li", title="Registration Year").get_text().strip()),
            "date_accessed": datetime.datetime.now().strftime('%Y-%m-%d'),
            "time_accessed": datetime.datetime.now().strftime('%H:%M:%S'),
            "colours": None,
            "area": None,
            "dealer": soup.select("a.e-dealer-link")[0].get_text(),
            "dealer_location": None,
            "dealer_link": domain + soup.select("a.e-dealer-link")[0].get("href"),
            "engine_power_max_kW": None,
            "engine_size_l": None,
            "engine_fuel_type": "p" if soup.find("li", title="Fuel Type").get_text().strip() == "Petrol" else "d",
            "engine_fuel_tank_l": None,
            "engine_transmission": "m" if soup.find("li", title="Transmission").get_text().strip() == "Manual" else "a",
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
            "features_usb": None,
            "features_aircon": None,
            "features_computer": None,
            "features_electric_windows": None,
            "features_cruise_control": None,
            "features_navigation": None,
            "specs_doors": None,
            "specs_tyres_front": None,
            "specs_tyres_back": None,
            "specs_power_steering": None,
            "specs_seats": None,
            "specs_kerb_weight": None,
            "specs_service_interval_km": None,
            "specs_central_locking": None,
            "previous_owners": None,
            "service_history": None,
            "warranty_remaining_months": None,
            "options": None,
            "description": [div.select("div")[0].text for div in soup.select("div") if
                            div.has_attr("data-reactroot") and len(div.select("div")) > 0][2],
        }

        basic_details = [[d.get_text() for d in div.select("div.col-6")] for div in soup.select("div.row") if
                         div.select("div.col-6")]
        data_dict = {item[0]: item[1] for item in basic_details if len(item) == 2}
        if data_dict.get("Previous Owners"):
            car["previous_owners"] = float(data_dict["Previous Owners"])
        if data_dict.get("Service History"):
            car["service_history"] = data_dict["Service History"]
        if data_dict.get("Manufacturers Colour"):
            car["colours"] = data_dict["Manufacturers Colour"]
        if data_dict.get("Warranty Remaining"):
            car["warranty_remaining_months"] = int(re.sub(r"\D", "", data_dict["Warranty Remaining"]))
        car["dealer_location"] = basic_details[0][0].split("|")[0].strip()

        # Figure out the accordian
        details = soup.select("div.e-accordion-body")
        divs = [item for sublist in details for item in sublist]
        data_dict = {div.select("span")[0].text: div.select("span")[1].text for div in divs}

        if data_dict.get("Fuel range (average)"):
            car["economy_fuel_range_km"] = float(re.sub(r"\D", "", data_dict["Fuel range (average)"]))
        if data_dict.get("CO2 emissions (average)"):
            car["economy_CO2_gpkm"] = float(re.sub(r"\D", "", data_dict["CO2 emissions (average)"]))
        if data_dict.get("No of doors"):
            car["specs_doors"] = float(re.sub(r"\D", "", data_dict["No of doors"]))
        if data_dict.get("Service interval distance"):
            car["specs_service_interval_km"] = float(re.sub(r"\D", "", data_dict["Service interval distance"]))
        if data_dict.get("Fuel consumption (average)"):
            car["economy_fuel_consumption_lpkm"] = float(
                re.sub(r" /100km", "", data_dict["Fuel consumption (average)"]).replace(",", "."))
        if data_dict.get("Engine size (litre)"):
            car["engine_size_l"] = float(re.sub(r" l", "", data_dict["Engine size (litre)"]).replace(",", "."))
        if data_dict.get("Power maximum (detail)"):
            car["engine_power_max_kW"] = float(re.sub(r" kW", "", data_dict["Power maximum (detail)"]))
        if data_dict.get("Acceleration 0-100 km/h"):
            car["performace_0_to_100_s"] = float(
                re.sub(r" s", "", data_dict["Acceleration 0-100 km/h"]).replace(",", "."))

        if data_dict.get("Maximum/top speed"):
            car["performace_speed_max_kmph"] = float(re.sub(r" km/h", "", data_dict["Maximum/top speed"]))
        if data_dict.get("Front tyres"):
            car["specs_tyres_front"] = data_dict["Front tyres"]
        if data_dict.get("Rear tyres"):
            car["specs_tyres_back"] = data_dict["Rear tyres"]
        if data_dict.get("Power steering"):
            car["specs_power_steering"] = data_dict["Power steering"]
        if data_dict.get("Seats (quantity)"):
            car["specs_seats"] = float(data_dict["Seats (quantity)"])
        if data_dict.get("Airbag quantity"):
            car["safety_airbag_quantity"] = float(data_dict["Airbag quantity"])
        if data_dict.get("Anti-lock braking system (ABS)"):
            car["safety_ABS"] = True
        if data_dict.get("Remote central locking"):
            car["specs_central_locking"] = "remote"
        if data_dict.get("Air conditioning"):
            car["features_aircon"] = True
        if data_dict.get("Electric windows"):
            car["features_electric_windows"] = True
        if data_dict.get("Bluetooth connectivity"):
            car["features_bluetooth"] = data_dict.get("Bluetooth connectivity")
        if data_dict.get("USB port"):
            car["features_usb"] = data_dict.get("USB port")

        if data_dict.get("Navigation"):
            car["features_navigation"] = data_dict.get("Navigation")
        if data_dict.get("Cruise control"):
            car["features_cruise_control"] = data_dict.get("Cruise control")
        if data_dict.get("On-board computer / multi-information display"):
            car["features_computer"] = True

        car["img_link"] = car["img_link"][0] if len(car["img_link"]) > 0 else None

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
        if car["colours"]:
            item = car["colours"].lower()
            for k, v in colours.items():
                if re.search(v, item):
                    actual_colours.append(k)
            if not actual_colours:
                actual_colours.append(item.replace(",", ""))
            car["colours"] = " ".join(actual_colours)

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
    # links = get_autotrader_links()
