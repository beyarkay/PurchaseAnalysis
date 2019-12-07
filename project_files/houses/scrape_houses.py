#!/usr/bin/python

import datetime
import os
import re

import pandas as pd
import requests
from bs4 import BeautifulSoup


def main():
    pass
    # carscoza_links = get_cars_links()
    # with open("houses_links.txt", "r") as read_file:
    #     carscoza_links = [line.strip() for line in read_file.readlines()]
    # populate_csv_from_carscoza(carscoza_links)


# def populate_csv_from_carscoza(carscoza_links):
#     domain = "https://www.cars.co.za"
#     car_dicts = []
#     print(f"Fetching data from {len(carscoza_links)} links")
#     for i, link in enumerate(carscoza_links):
#
#         if i % 50 == 0 and i > 0:
#             print()
#         if i % 10 == 0:
#             print(f"({i:03})", end="")
#         print(".", end="")
#         soup = BeautifulSoup(requests.get(link).text, features="html.parser")
#
#         # predefine the dictionary because it's the easiest way to ensure the dataframe is in a decent order
#         car = {
#             "website_id": re.search("\(ID:(\d+)\)", soup.title.text).groups()[0],
#             "price":
#                 float(re.sub(r"\D", "", soup.find("div", class_="price").text)),
#             "heading":
#                 re.sub("\s", " ", soup.find("h1", class_="heading").text.strip()),
#             "link":
#                 link,
#             "img_link":
#                 [link.get("src") for link in soup.find_all("img", class_="gallery__slider-image") if
#                  link.has_attr("src")],
#             "make":
#                 [link.text.split("\n \n") for link in soup.find_all("div", class_="js-breadcrumbs")][0][2].lower(),
#             "model":
#                 [link.text.split("\n \n") for link in soup.find_all("div", class_="js-breadcrumbs")][0][3].lower(),
#             "odometer_km": None,
#             "year": None,
#             "date_accessed": datetime.datetime.now().strftime('%Y_%m_%d'),
#             "time_accessed": datetime.datetime.now().strftime('%H:%M:%S'),
#             "colours": None,
#             "area": None,
#             "dealer": None,
#             "dealer_location": None,
#             "dealer_link": None,
#             "engine_power_max_kW": None,
#             "engine_size_l": None,
#             "engine_fuel_type": None,
#             "engine_fuel_tank_l": None,
#             "engine_transmission": None,
#             "performace_0_to_100_s": None,
#             "performace_speed_max_kmph": None,
#             "economy_fuel_consumption_lpkm": None,
#             "economy_fuel_range_km": None,
#             "economy_CO2_gpkm": None,
#             "safety_ABS": None,
#             "safety_EBD": None,
#             "safety_brake_assist": None,
#             "safety_driver_airbag": None,
#             "safety_passenger_airbag": None,
#             "safety_airbag_quantity": None,
#             "features_bluetooth": None,
#             "features_aircon": None,
#             "specs_doors": None,
#             "specs_seats": None,
#             "specs_kerb_weight": None,
#             "options": None,
#             "description": None,
#         }
#         dealer_location = soup.select(".number-tracker__address")
#         if dealer_location:
#             car["dealer_location"] = dealer_location[0].text.strip()
#         dealer = soup.select(".heading.heading_centered.number-tracker__name")
#         if dealer:
#             car["dealer"] = dealer[0].text.strip()
#         elif soup.select(".vehicle-view__content-links.vehicle-view__content-links_blue"):
#             car["dealer"] = soup.select(".vehicle-view__content-links.vehicle-view__content-links_blue")[0].text.strip()
#         elif "private" in soup.select(".lead-form__title")[0].text.lower():
#             car["dealer"] = "Private"
#
#
#         dealer_link = soup.select(".vehicle-view__content-links.vehicle-view__content-links_blue")
#         if dealer_link:
#             car["dealer_link"] = domain + dealer_link[0].get("href")
#         elif soup.select(".bbtn.btn-primary.button.button_size_small.button_side-pad_medium.stock-reel__view-btn"):
#             car["dealer_link"] = domain + soup.select(
#                 ".bbtn.btn-primary.button.button_size_small.button_side-pad_medium.stock-reel__view-btn")[0].get(
#                 "href")
#         car["img_link"] = car["img_link"][0] if len(car["img_link"]) > 0 else None
#
#         keys = [link.text for link in soup.find_all("td", class_="vehicle-details__label")]
#         values = [link.text for link in soup.find_all("td", class_="vehicle-details__value")]
#         data_dict = {key: value for key, value in zip(keys, values)}
#
#         # normalise the colours to be something workable
#         colours = {
#             "white": re.compile("(white)"),
#             "grey": re.compile("(grey|gray|charcoal)"),
#             "silver": re.compile("(silver)"),
#             "black": re.compile("(black)"),
#             "nan": re.compile("(nan)"),
#             "blue": re.compile("(blue|sea)"),
#             "orange": re.compile("(orange)"),
#             "red": re.compile("(pepper|red)"),
#         }
#         actual_colours = []
#         if data_dict.get("Colour"):
#             item = data_dict.get("Colour").lower()
#             for k, v in colours.items():
#                 if re.search(v, item):
#                     actual_colours.append(k)
#             if not actual_colours:
#                 actual_colours.append(item.replace(",", ""))
#             car["colours"] = " ".join(actual_colours)
#
#         car["odometer_km"] = re.sub(r"\D", "", data_dict.get("Mileage")) if data_dict.get("Mileage") else None
#         car["odometer_km"] = float(car["odometer_km"]) if len(car["odometer_km"]) > 0 else None
#         car["year"] = float(data_dict.get("Year")) if data_dict.get("Year") else None
#         car["area"] = data_dict.get("Area").lower() if data_dict.get("Area") else None
#         car["engine_transmission"] = data_dict.get("Transmission").strip()[0].lower() if data_dict.get(
#             "Transmission") else None
#         car["engine_fuel_type"] = data_dict.get("Fuel Type").strip()[0].lower() if data_dict.get(
#             "Fuel Type") else None
#         car["options"] = data_dict.get("Options") if data_dict.get("Options") else None
#
#         car["description"] = \
#             [link.text.strip() for link in soup.find_all("div", class_="vehicle-view__content")]
#         car["description"] = car["description"][0] if len(car["description"]) > 0 else None
#         # First extract the table from the webpage
#         table_data = [[td.text for td in link.find_all("td")] for link in
#                       soup.find_all("table", class_="vehicle-specs__table")]
#         # Then put the key-value pairs together into tuples
#         zipped_data = [list(zip(sub_list[0::2], sub_list[1::2])) for sub_list in table_data]
#         # Then flatten the list of lists to be just one long list
#         flat_list = [item for sublist in zipped_data for item in sublist]
#         # finally, convert the list of tuples into a dict
#         data_dict = dict(flat_list)
#         # And now add the data into the car dict
#         car["economy_fuel_consumption_lpkm"] = float(
#             data_dict.get("Average").replace("l/100km", "").strip()) if data_dict.get("Average") else None
#         car["engine_power_max_kW"] = float(
#             data_dict.get("Power Max").replace("Kw", "").strip()) if data_dict.get("Power Max") else None
#         car["engine_size_l"] = float(data_dict.get("Engine Size").replace("l", "").strip()) if data_dict.get(
#             "Power Max") else None
#         car["engine_fuel_tank_l"] = float(
#             data_dict.get("Fuel tank capacity").replace("l", "").strip()) if data_dict.get(
#             "Fuel tank capacity") else None
#         car["performace_0_to_100_s"] = float(
#             data_dict.get("0-100Kph").replace("s", "").strip()) if data_dict.get("0-100Kph") and data_dict.get(
#             "0-100Kph").replace("s", "").strip().replace(".", "", 1).isdigit() else None
#         car["performace_speed_max_kmph"] = float(
#             data_dict.get("Top speed").replace("Km/h", "").strip()) if data_dict.get("Top speed") else None
#         car["economy_fuel_range_km"] = float(
#             data_dict.get("Fuel range").replace("Km", "").replace(" ", "").strip()) if data_dict.get(
#             "Fuel range") else None
#         car["economy_CO2_gpkm"] = float(data_dict.get("Co2").replace("g/km", "").strip()) if data_dict.get(
#             "Co2") else None
#         car["safety_ABS"] = True if data_dict.get("ABS") else False
#         car["safety_EBD"] = True if data_dict.get("EBD") else False
#         car["safety_brake_assist"] = True if data_dict.get("Brake assist") else False
#         car["safety_driver_airbag"] = True if data_dict.get("Driver airbag") else False
#         car["safety_passenger_airbag"] = True if data_dict.get("Passenger airbag") else False
#         car["safety_airbag_quantity"] = float(data_dict.get("Airbag quantity").strip()[0]) if data_dict.get(
#             "Airbag quantity") else None
#         car["features_bluetooth"] = True if data_dict.get("Bluetooth connectivity") else False
#         car["features_aircon"] = True if data_dict.get("Air conditioning") else False
#         car["specs_doors"] = float(data_dict.get("Doors").strip()) if data_dict.get("Doors") else None
#         car["specs_seats"] = float(data_dict.get("Seats quantity").replace("l", "").strip()) if data_dict.get(
#             "Seats quantity") else None
#         car["specs_kerb_weight"] = float(
#             data_dict.get("Kerb weight").replace("Kg", "").split("-")[0].strip()) if data_dict.get(
#             "Kerb weight") else None
#         car["specs_central_locking"] = data_dict.get("Central locking").strip().lower() if data_dict.get(
#             "Central locking") else None
#         car_dicts.append(car)
#     print(" done")
#
#     df = pd.DataFrame(car_dicts)
#     path = f"cars.csv"
#     print(f"Saving data to {path}")
#     print(df.describe())
#     with open(path, 'a') as f:
#         df.to_csv(f, header=False, encoding='utf-8')


# def get_cars_links():
#     url = "https://www.cars.co.za/searchVehicle.php?new_or_used=Used&make_model=&vfs_area=Western+Cape&agent_locality=&price_range=50000+-+74999%7C75000+-+99999%7C100000+-+124999%7C125000+-+149999&os=&locality=&body_type_exact=Hatchback&transmission=&fuel_type=&login_type=&mapped_colour=black%7Cgrey%7Csilver&vfs_year=&vfs_mileage=&vehicle_axle_config=&keyword=&sort=vfs_price&P=1"
#     domain = "https://www.cars.co.za"
#     print(domain, end=" ")
#     car_links = []
#     while True:
#         print(".", end="")
#         request = requests.get(url)
#         page = BeautifulSoup(request.text, features="html.parser")
#
#         # Store all the links to cars from the current page
#         car_links.extend(
#             [domain + link.get("href") for link in page.find_all("a", class_="vehicle-list__vehicle-name")])
#
#         # Find the link to the next page
#         next_page_links = page.select(".pagination__nav.fa-right-open-big")
#         if next_page_links:
#             url = domain + next_page_links[0].get("href")
#         else:
#             print(f" ({len(car_links)} cars found)")
#             path = "car_links.txt"
#             with open(path, "w+") as write_file:
#                 write_file.write("\n".join(car_links))
#
#             return car_links

if __name__ == '__main__':
    main()
