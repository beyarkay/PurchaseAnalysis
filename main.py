import datetime
import glob
import os
import re
import time
import matplotlib.pyplot as plt
import pandas as pd
import requests
import statsmodels.api as sm
# import scipy as sp
from bs4 import BeautifulSoup
from matplotlib import rcParams
from matplotlib.ticker import EngFormatter

RE_NO_BREAK_SPACE = re.compile(r"( )")
KEYS = []
NOW = datetime.datetime.now().strftime('%Y_%m_%d')
COLOURS = ['#db5f57', '#dbc257', '#91db57', '#57d3db', '#5770db', '#a157db', '#db57b2']
URLS_P24 = [
    "https://www.property24.com/for-sale/sea-point/cape-town/western-cape/11021",
    "https://www.property24.com/for-sale/observatory/cape-town/western-cape/10157",
    "https://www.property24.com/for-sale/gardens/cape-town/western-cape/9145",
    "https://www.property24.com/for-sale/cape-town-city-centre/cape-town/western-cape/9138",
    "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682",
    "https://www.property24.com/for-sale/muizenberg/cape-town/western-cape/9025",
    "https://www.property24.com/for-sale/constantia/cape-town/western-cape/11742",
    "https://www.property24.com/for-sale/woodstock/cape-town/western-cape/10164",
    "https://www.property24.com/for-sale/newlands/cape-town/western-cape/8679",
    "https://www.property24.com/for-sale/green-point/cape-town/western-cape/11017",
    "https://www.property24.com/for-sale/claremont-upper/cape-town/western-cape/14225",
    "https://www.property24.com/for-sale/plumstead/cape-town/western-cape/10094",
    "https://www.property24.com/for-sale/camps-bay/cape-town/western-cape/11014",
    "https://www.property24.com/for-sale/claremont/cape-town/western-cape/11741",
    "https://www.property24.com/for-sale/fresnaye/cape-town/western-cape/11016"
]
"""
Car minimum specifications:
    Area: Western Cape
    Price: 50 000 - 150 000
    Condition: Used
    Body Type: Hatchback
    Colour: White, Silver, Grey, Black

"""

URLS_CARS = [
    "https://www.cars.co.za/searchVehicle.php?new_or_used=Used&make_model=&vfs_area=Western+Cape&agent_locality=&price_range=50000+-+74999%7C75000+-+99999%7C100000+-+124999%7C125000+-+149999&os=&locality=&body_type_exact=Hatchback&transmission=&fuel_type=&login_type=&mapped_colour=black%7Cgrey%7Csilver&vfs_year=&vfs_mileage=&vehicle_axle_config=&keyword=&sort=vfs_price",
]

URLS_AUTOTRADER = [
    "https://www.autotrader.co.za/cars-for-sale/western-cape/p-9?price=50001-to-200000&bodytype=hatchback&bodytype=sedan&colour=Black&colour=Grey&colour=Silver&colour=White&isused=True",
]

URLS_WEBUYCARS = [
    "https://www.webuycars.co.za/buy-a-car?subcategory=Hatchback&DealerKey=%5B%22Cape%20Town%202%20Phumelela%20Park%20Branch%22,%22Cape%20Town%201%20Montague%20Drive%20Branch%22%5D&Priced_Amount_Gte=50000&Priced_Amount_Lte=150000&BodyType=%5B%22Hatchback%22%5D&Colour=%5B%22Silver%22,%22White%22,%22Grey%22,%22Black%22%5D&page=1"
]

IN_DEVELOPMENT = True


def main():
    global NOW
    if IN_DEVELOPMENT:

        # download_autotrader_html(URLS_AUTOTRADER)
        # download_cars_html(URLS_CARS)
        # download_webuycars_html(URLS_WEBUYCARS)
        NOW = "2019_11_21"

        file_paths = sorted(glob.glob(f"_data/{NOW}/*"))
        if len(file_paths) == 0:
            print(f"Warning: len(file_paths) == 0 from '_data/{NOW}/*'")
        extract_and_save_cars(file_paths)
        csvs = sorted(glob.glob(f"CSVs/{NOW}/*"))

        if len(csvs) == 0:
            print(f"Warning: len(csvs) == 0 from 'CSVs/{NOW}/*'")

        prune_records(csvs[0], ["year", "performace_0_to_100_s", "economy_fuel_consumption_lpkm"], "price")
        # csvs = sorted(glob.glob(f"CSVs/{NOW}/*"))
        # plot_csv(
        #     "CSVs/2019_11_21/www.cars.co.za_pruned.csv",
        #     ["year", "performace_0_to_100_s", "economy_fuel_consumption_lpkm"],
        #     "price",
        #     should_annotate=False,
        #     save_figure=False)


    else:
        download_p24_html(URLS_P24)
        file_paths = sorted(glob.glob(f"_data/{NOW}/*"))
        extract_and_save_houses(file_paths)
        csvs = sorted(glob.glob(f"CSVs/{NOW}/*"))

        for csv in csvs:
            plot_csv(csv,
                     ["bedrooms", "bathrooms", "garages", "erf size", "floor size"],
                     "price", save_figure=True)


def download_cars_html(urls):
    domain = "www.cars.co.za"
    print(domain, end="")
    for url in urls:
        request = requests.get(url)
        page = BeautifulSoup(request.text, features="html.parser")

        path = f"_data/{NOW}/{domain}/P=1.html"
        directory = os.sep.join(path.split(os.sep)[:-1])

        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, "w+") as write_file:
            write_file.write(request.text)

        num_pages = 0
        should_continue = True
        while should_continue:
            should_continue = False
            for link in page.find_all('a'):
                """
                <a class="pagination__page pagination__nav js-pagination fa fa-right-open-big" 
                href="/searchVehicle.php?new_or_used=Used&amp;make_model=&amp;vfs_area=Western+Cape&amp;agent_locality=&amp;price_range=50000+-+74999%7C75000+-+99999%7C100000+-+124999%7C125000+-+149999&amp;os=&amp;locality=&amp;body_type_exact=Hatchback&amp;transmission=&amp;fuel_type=&amp;login_type=&amp;mapped_colour=black%7Cgrey%7Csilver&amp;vfs_year=&amp;vfs_mileage=&amp;vehicle_axle_config=&amp;keyword=&amp;sort=vfs_price&amp;P=2"
                ></a>
                """
                if "pagination__nav" in link.get_attribute_list("class") \
                        and "fa-right-open-big" in link.get_attribute_list("class"):
                    # Note that cars.co.za has two of these, but we only care about the one at the top of the page
                    request = requests.get("https://" + domain + link.get('href'))

                    path = f"_data/{NOW}/{domain}/{request.url.split('&')[-1]}.html"
                    directory = os.sep.join(path.split(os.sep)[:-1])

                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    with open(path, "w+") as write_file:
                        write_file.write(request.text)

                    page = BeautifulSoup(request.text, features="html.parser")
                    should_continue = True
                    num_pages += 1
                    print(".", end="")
                    break
        print(f" done; {num_pages} pages from:\t{url}")


def download_autotrader_html(urls):
    domain = "www.autotrader.co.za"
    print(domain, end="")
    for url in urls:
        request = requests.get(url)
        page = BeautifulSoup(request.text, features="html.parser")

        path = f"_data/{NOW}/{domain}/pagenumber=1.html"
        directory = os.sep.join(path.split(os.sep)[:-1])

        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, "w+") as write_file:
            write_file.write(request.text)

        num_pages = 0
        should_continue = True
        while should_continue:
            should_continue = False
            for link in page.find_all('a'):
                """
                <a class="gm-float-right e-pagination-link" 
                href="/cars-for-sale/western-cape/p-9?pagenumber=2&amp;price=50001-to-200000&amp;bodytype=hatchback&amp;bodytype=sedan&amp;colour=Black&amp;colour=Grey&amp;colour=Silver&amp;colour=White&amp;isused=True">
                <img src="/Common/Content/Images/Icons/arrow-right.svg" alt="Next"
                ></a>
                """
                if "gm-float-right" in link.get_attribute_list("class") \
                        and "e-pagination-link" in link.get_attribute_list("class") \
                        and "m-disabled" not in link.get_attribute_list("class"):
                    request = requests.get("https://" + domain + link.get('href'))

                    path = f"_data/{NOW}/{domain}/{request.url.split('?')[1].split('&')[0]}.html"
                    directory = os.sep.join(path.split(os.sep)[:-1])

                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    with open(path, "w+") as write_file:
                        write_file.write(request.text)

                    page = BeautifulSoup(request.text, features="html.parser")
                    should_continue = True
                    num_pages += 1
                    print(".", end="")
                    break
        print(f" done; {num_pages} pages from:\t{url}")


def download_webuycars_html(urls):
    domain = "www.webuycars.co.za"
    print(domain, end="")
    for url in urls:
        request = requests.get(url)
        path = f"_data/{NOW}/{domain}/page=1.html"
        directory = os.sep.join(path.split(os.sep)[:-1])

        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, "w+") as write_file:
            write_file.write(request.text)

        num_pages = 0
        while True:
            # This website has some really cancerous coders. Trying to go to page=99 will return 200 and '(Showing 2353 - 2352 of 94)'
            request = requests.get(url.replace("page=1", f"page={num_pages + 1}"))
            if num_pages > 4:
                break

            path = f"_data/{NOW}/{domain}/{request.url.split('&')[-1]}.html"
            directory = os.sep.join(path.split(os.sep)[:-1])

            if not os.path.exists(directory):
                os.makedirs(directory)
            with open(path, "w+") as write_file:
                write_file.write(request.text)

            num_pages += 1
            print(".", end="")
        print(f" done; {num_pages} pages from:\t{url}")


def download_p24_html(urls):
    for url in urls:
        request = requests.get(url)
        page = BeautifulSoup(request.text, features="html.parser")

        split_url = request.url.replace('https://', '').split('/')
        print(f"{split_url[2].capitalize()}", end="")
        path = f"_data/{NOW}/{'_'.join(split_url)}/p1.html"
        directory = os.sep.join(path.split(os.sep)[:-1])

        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, "w+") as write_file:
            write_file.write(request.text)

        num_pages = 0
        should_continue = True
        while should_continue:
            should_continue = False
            for link in page.find_all('a'):
                if url.split("/")[2] == "www.property24.com":
                    if "Next" in link.text and "javascript" not in link.get('href') and link.has_attr(
                            "data-pagenumber"):
                        request = requests.get(link.get('href'))

                        split_url = request.url.replace('https://', '').split('/')
                        path = f"_data/{NOW}/{'_'.join(split_url[:-1])}/{split_url[-1]}.html"
                        directory = os.sep.join(path.split(os.sep)[:-1])

                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        with open(path, "w+") as write_file:
                            write_file.write(request.text)

                        page = BeautifulSoup(request.text, features="html.parser")
                        should_continue = True
                        num_pages += 1
                        print(".", end="")
                        break
                elif url.split("/")[2] == "www.cars.co.za":
                    """
                    <a class="pagination__page pagination__nav js-pagination fa fa-right-open-big" 
                    href="/searchVehicle.php?new_or_used=Used&amp;make_model=&amp;vfs_area=Western+Cape&amp;agent_locality=&amp;price_range=50000+-+74999%7C75000+-+99999%7C100000+-+124999%7C125000+-+149999&amp;os=&amp;locality=&amp;body_type_exact=Hatchback&amp;transmission=&amp;fuel_type=&amp;login_type=&amp;mapped_colour=black%7Cgrey%7Csilver&amp;vfs_year=&amp;vfs_mileage=&amp;vehicle_axle_config=&amp;keyword=&amp;sort=vfs_price&amp;P=2"
                    ></a>
                    """
                    if "pagination__nav" in link.get_attribute_list(
                            "class") and "fa-right-open-big" in link.get_attribute_list("class"):
                        # Note that cars.co.za has two of these, but we only care about the one at the top of the page
                        request = requests.get("https://www.cars.co.za" + link.get('href'))

                        path = f"_data/{NOW}/www.cars.co.za/{request.url.split('&')[-1]}.html"
                        directory = os.sep.join(path.split(os.sep)[:-1])

                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        with open(path, "w+") as write_file:
                            write_file.write(request.text)

                        page = BeautifulSoup(request.text, features="html.parser")
                        should_continue = True
                        num_pages += 1
                        print(".", end="")
                        break

                        pass
                elif url.split("/")[2] == "www.autotrader.co.za":
                    pass
                elif url.split("/")[2] == "www.webuycars.co.za":
                    pass
        print(f" done; {num_pages} pages from:\t{url}")


def extract_and_save_cars(directories):
    def extract_cars_from_soup(soup, cars=None, car_id=0):
        if cars is None:
            cars = []

        """
        <a href="/for-sale/used/2012-TATA-Indica-1.4-Le-Western-Cape/5267659/" 
        class="vehicle-list__vehicle-name">
        TATA Indica 1.4 Le </a>
        """

        for i, link in enumerate(soup.find_all("a", class_="vehicle-list__vehicle-name")):
            car = {
                "id": None,
                "price": None,
                "heading": None,
                "link": None,
                "img_link": None,
                "make": None,
                "model": None,
                "odometer_km": None,
                "year": None,
                "date_accessed": None,
                "time_accessed": None,
                "colour": None,
                "location": None,
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
                "history_num_owners": None,
                "options": None,
                "description": None,
            }
            car_page = BeautifulSoup(requests.get("https://" + domain + link.get("href")).text, features="html.parser")
            if domain == "www.cars.co.za":
                car["id"] = car_id
                car["price"] = float(re.sub(r"\D", "", car_page.find("div", class_="price").text))
                car["heading"] = re.sub("\s", " ", car_page.find("h1", class_="heading").text.strip())
                car["link"] = domain + link.get("href")
                # car["img_links"] = [link.get("data-src") for link in
                #                     car_page.find_all("img", class_="gallery__slider-image") if
                #                     link.has_attr("data-src")]
                car["img_link"] = [link.get("src") for link in car_page.find_all("img", class_="gallery__slider-image")
                                   if link.has_attr("src")]
                car["img_link"] = car["img_link"][0] if len(car["img_link"]) > 0 else None
                car["make"] = \
                    [link.text.split("\n \n") for link in car_page.find_all("div", class_="js-breadcrumbs")][0][2]
                car["make"] = car.get("make").lower()
                car["model"] = \
                    [link.text.split("\n \n") for link in car_page.find_all("div", class_="js-breadcrumbs")][0][3]
                car["model"] = car.get("model").lower()
                keys = [link.text for link in car_page.find_all("td", class_="vehicle-details__label")]
                values = [link.text for link in car_page.find_all("td", class_="vehicle-details__value")]
                data_dict = {key: value for key, value in zip(keys, values)}
                car["odometer_km"] = re.sub(r"\D", "", data_dict.get("Mileage")) if data_dict.get("Mileage") else None
                car["odometer_km"] = float(car["odometer_km"]) if len(car["odometer_km"]) > 0 else None
                car["year"] = float(data_dict.get("Year")) if data_dict.get("Year") else None
                car["colour"] = data_dict.get("Colour").lower() if data_dict.get("Colour") else None
                car["colour"] = car.get("colour").lower()
                car["location"] = data_dict.get("Area").lower() if data_dict.get("Area") else None
                car["location"] = car.get("location").lower()
                car["engine_transmission"] = data_dict.get("Transmission").strip()[0].lower() if data_dict.get(
                    "Transmission") else None
                car["engine_fuel_type"] = data_dict.get("Fuel Type").strip()[0].lower() if data_dict.get(
                    "Fuel Type") else None
                car["options"] = data_dict.get("Options") if data_dict.get("Options") else None
                car["description"] = \
                    [link.text.strip() for link in car_page.find_all("div", class_="vehicle-view__content")]
                car["description"] = car["description"][0] if len(car["description"]) > 0 else None
                # First extract the table from the webpage
                table_data = [[td.text for td in link.find_all("td")] for link in
                              car_page.find_all("table", class_="vehicle-specs__table")]
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
            elif domain == "www.autotrader.co.za":
                pass
            elif domain == "www.webuycars.co.za":
                pass
            print(".", end="")
            cars.append(car)
            car_id += 1

        return cars, car_id

    car_id = 0
    cars = []
    for directory in directories:
        domain = directory.split("/")[-1]
        print(f"Extracting data from: '{directory}'")
        data_start_time = (round(time.time(), 3))
        pages = sorted(glob.glob(directory + os.sep + "*"))
        for page in pages:
            soup_start_time = (round(time.time(), 3))
            print(f"\tExtracting soup from '{page}'\n\t", end="")
            soup = BeautifulSoup(open(page), features='html.parser')
            cars, car_id = extract_cars_from_soup(soup, cars=cars, car_id=car_id)
            print(f" Done: {round(round(time.time(), 3) - soup_start_time, 3)}s")
        print(f"Done: {round(round(time.time(), 3) - data_start_time, 3)}s total")

        df = pd.DataFrame(cars)
        the_order = [
            "id",
            "price",
            "heading",
            "link",
            "make",
            "model",
            "odometer_km",
            "year",
            "colour",
            "location",
            "engine_power_max_kW",
            "engine_size_l",
            "engine_fuel_type",
            "engine_fuel_tank_l",
            "engine_transmission",
            "performace_0_to_100_s",
            "performace_speed_max_kmph",
            "economy_fuel_consumption_lpkm",
            "economy_fuel_range_km",
            "economy_CO2_gpkm",
            "safety_ABS",
            "safety_EBD",
            "safety_brake_assist",
            "safety_driver_airbag",
            "safety_passenger_airbag",
            "safety_airbag_quantity",
            "features_bluetooth",
            "features_aircon",
            "specs_doors",
            "specs_seats",
            "specs_kerb_weight",
            "history_num_owners",
            "options",
            "description",
            "img_link",

        ]
        the_order = [col_name for col_name in the_order if col_name in list(df.columns)]
        df = df[the_order]

        path = f"CSVs/{os.sep.join(directory.split(os.sep)[1:])}.csv"
        directory = os.sep.join(path.split(os.sep)[:-1])
        if not os.path.exists(directory):
            os.makedirs(directory)
        df.to_csv(path, encoding='utf-8')


def extract_and_save_houses(directories):
    for directory in directories:
        print(f"Extracting soup from '{directory}'")
        pages = sorted(glob.glob(directory + os.sep + "*"))
        houses = []
        house_id = 0
        for page in pages:
            print(f"\tExtracting soup from '{page}'")
            soup = BeautifulSoup(open(page), features='html.parser')
            houses, house_id = extract_houses_from_soup(soup, houses=houses, house_id=house_id)

        df = pd.DataFrame(houses)
        the_order = ["id",
                     "link",
                     "date",
                     "price",
                     "bedrooms",
                     "bathrooms",
                     "garages",
                     "erf size",
                     "floor size",
                     "address",
                     "description",
                     "location"]
        the_order = [col_name for col_name in the_order if col_name in list(df.columns)]
        df = df[the_order]

        path = f"CSVs/{os.sep.join(directory.split(os.sep)[1:])}.csv"
        directory = os.sep.join(path.split(os.sep)[:-1])
        if not os.path.exists(directory):
            os.makedirs(directory)
        df.to_csv(path, encoding='utf-8')


def extract_houses_from_soup(soup, houses=None, house_id=0):
    # TODO sometimes property24 doesn't actually have their data in this format. See gardens 2019_11_19

    if houses is None:
        houses = []
    for i, house_data in enumerate(soup.find_all("div", class_="p24_content")):
        house = {}
        # print(f"Evaluating house: 'https://www.property24.com{house_data.parent['href']}")
        price = house_data.find("div", class_="p24_price")
        price = format_numbers(normalise_from_find(price))
        description = house_data.find("div", class_="p24_description")
        if price and description:
            if house_data.parent.has_attr("href"):
                house["link"] = "https://www.property24.com" + house_data.parent["href"]

            house["address"] = house_data.find("div", class_="p24_address")
            icons = house_data.find("div", class_="p24_icons")
            attribs = icons.find_all("span")
            for j, attrib in enumerate(attribs):
                if attrib.has_attr("title"):
                    house[attrib["title"].lower()] = attrib.find("span").text

            house["price"] = price
            house["date"] = datetime.datetime.now().strftime('%Y_%m_%d')
            house["description"] = normalise_from_find(description)
            location = description.find("span", class_="p24_location")
            house["location"] = normalise_from_find(location)

            if house.get("bathrooms"):
                house["bathrooms"] = format_numbers(house["bathrooms"])
            if house.get("bedrooms"):
                house["bedrooms"] = format_numbers(house["bedrooms"])
            if house.get("erf size"):
                house["erf size"] = format_numbers(house["erf size"])
            if house.get("floor size"):
                house["floor size"] = format_numbers(house["floor size"])
            if house.get("garages"):
                house["garages"] = format_numbers(house["garages"])
        if len(house) != 0:
            house["id"] = house_id
            house_id += 1
            houses.append(house)
        else:
            # Usually, this means that either the price or description weren't valid
            print(f"\t\tIgnored: https://www.property24.com{house_data.parent['href']}")
    return houses, house_id


def plot_csv(csv_path, x_dims, y_dim, should_annotate=True, save_figure=False):
    # TODO add date_retrieved to the graph itself
    print(f"Plotting '{csv_path}'")
    rcParams.update({'figure.dpi': 200})
    df = pd.read_csv(csv_path)
    x_dims = df.columns.intersection(x_dims)
    x = df[x_dims]
    y = df[y_dim]

    # TODO if there's <2 datapoints, just draw a table instead of a graph

    print(f"\tDrawing scatter dots and regression line")
    # make the axes, and plot the data
    fig, axes = plt.subplots(len(x_dims) + 1,
                             figsize=(7, 5 * (len(x_dims) + 1)))

    for i, x_dim in enumerate(x_dims):
        # Add Least Squares Line and r-squared value
        regression_line = df[[x_dim, y_dim]].dropna()

        label = f"{x_dim.title()}: n={x[x_dim].dropna().size}"
        # Check to see if there's enough data to plot the regression line
        if regression_line[x_dim].max() != regression_line[x_dim].min():
            linreg = sp.stats.linregress(regression_line[x_dim], regression_line[y_dim])
            axes[i].plot(regression_line[x_dim],
                         linreg.intercept + linreg.slope * regression_line[x_dim],
                         color=COLOURS[i])
            label += f", $r^2$={round(linreg.rvalue ** 2, 2)}"

            max_minus_min = (regression_line[x_dim].max() - regression_line[x_dim].min())
            regression_line[x_dim] = (regression_line[x_dim] - regression_line[x_dim].min()) / max_minus_min
            linreg = sp.stats.linregress(regression_line[x_dim], regression_line[y_dim])
            axes[-1].plot(regression_line[x_dim],
                          linreg.intercept + linreg.slope * regression_line[x_dim],
                          color=COLOURS[i])
            axes[-1].scatter(regression_line[x_dim],
                             regression_line[y_dim],
                             label=label,
                             color=COLOURS[i],
                             s=10,
                             alpha=0.5)

        axes[i].scatter(x[x_dim],
                        y,
                        label=label,
                        color=COLOURS[i],
                        s=30)

    print(f"\tDrawing labels")
    if "www.property24.com" in csv_path.split(os.sep)[-1]:
        suburb = " \nin " + csv_path.split(os.sep)[-1].split("_")[2].replace("-", " ").title()
    else:
        suburb = ""
    # First put labels onto the separate axes
    for i, x_dim in enumerate(x_dims):
        axes[i].set_xlabel(x_dim.title())
        axes[i].set_ylabel(y_dim.title())
        axes[i].set_title(f"{x_dim.title()} vs {y_dim.title()}{suburb}")

    # Then put labels onto the last plot
    x_label = " & ".join([x_dim.title() for x_dim in x_dims]) + " (normalised)"
    axes[-1].set_xlabel(x_label)
    axes[-1].set_ylabel(y_dim.title())
    axes[-1].set_title(f"{x_label} vs {y_dim.title()} \nin {suburb}")

    text = []

    if should_annotate:
        print(f"\tDrawing annotations")
        for i, row in df.iterrows():
            for j, x_dim in enumerate(x_dims):
                axes[j].annotate(row["id"],
                                 xy=(row[x_dim] * 1.015, y[i]),
                                 size=8,
                                 va='center',
                                 alpha=0.6)

                if df[x_dim].max() != df[x_dim].min():
                    x_norm = (row[x_dim] - df[x_dim].min()) / (df[x_dim].max() - df[x_dim].min())
                    axes[-1].annotate(row["id"],
                                      xy=(x_norm, y[i]),
                                      size=5,
                                      va='center',
                                      ha='center',
                                      alpha=0.6)

    print(f"\tFormatting axes")
    for ax in axes:
        # add gridlines
        ax.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.7)

        # add ticks and number formatting
        ax.yaxis.set_major_formatter(EngFormatter())
        ax.minorticks_on()
        ax.tick_params(axis='both', which='minor')

        # add legend
        ax.legend(loc='best')

    # fig.suptitle(f"{x_label} vs {y_dim.title()} \nin {suburb}", fontsize=16)
    fig.tight_layout()
    if save_figure:
        path = f"graphs/{os.sep.join(csv_path.split(os.sep)[1:])}".replace(".csv", ".png")
        directory = os.sep.join(path.split(os.sep)[:-1])

        if not os.path.exists(directory):
            os.makedirs(directory)
        print(f"\tSaving graph to '{path}'")
        plt.savefig(path)
    else:
        plt.show()


def prune_records(csv_path, x_dims, y_dim):
    # TODO it might be better to refactor this into two functions: one function
    #  that evaluates a record, and another that applies that evaluation
    #  to the csv file

    print(f"Getting deals from '{csv_path}'")
    df = pd.read_csv(csv_path)
    x_dims = df.columns.intersection(x_dims)

    best_deals = df[df.columns]

    for i, x_dim in enumerate(x_dims):
        regression_line = df[[x_dim, y_dim]].dropna()

        if regression_line[x_dim].max() != regression_line[x_dim].min():
            linreg = sp.stats.linregress(regression_line[x_dim], regression_line[y_dim])
            deals = df[df[y_dim] < (linreg.intercept + linreg.slope * df[x_dim])]
            best_deals = pd.merge(
                best_deals,
                deals,
                how='inner')
    path = f"{'.'.join(csv_path.split('.')[:-1])}_pruned.csv"

    best_deals.to_csv(path, encoding='utf-8')


def draw_records(csv_path, x_dims, y_dim):
    print(f"Drawing records from '{csv_path}'")
    df = pd.read_csv(csv_path)
    if len(df.index) > 20 and input(f"Number of records = '{len(df.index)}' (>20). Continue? [y/n]: ") != "y":
        return
    x_dims = df.columns.intersection(x_dims)


def format_numbers(s):
    s = str(s).replace("m²", "").replace(" ", "").replace("R", "").strip()
    if s.replace(".", "", 1).isdigit():
        return float(s)
    else:
        # print(f"Warning, {s} is not a number, returning None")
        return None


def get_icon_attr(icons, attr):
    attribute = icons.find("span", class_="p24_featureDetails", title=attr)
    if attribute:
        return attribute.find("span").text
    else:
        return "Unknown"


def normalise_from_find(s):
    return re.sub(RE_NO_BREAK_SPACE, "", s.text.strip())


if __name__ == '__main__':
    main()
