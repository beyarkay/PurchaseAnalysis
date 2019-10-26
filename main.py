from bs4 import BeautifulSoup
import requests
import re
from pprint import pprint as pprint

import statsmodels.api as sm
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

URL = "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682"
RE_NO_BREAK_SPACE = re.compile(r"( )")
KEYS = []


def main():
    houses = get_property24_houses(URL)
    print(KEYS)

    x_keys = ["bedrooms", "bathrooms"]
    y_key = "price"

    fig, axes = plt.subplots(ncols=1, nrows=2, figsize=(8, 12))
    plot_xy(x_keys[0], y_key, houses, axes[0])
    plot_xy(x_keys[1], y_key, houses, axes[1])

    plt.show()
    print_links(houses)


def print_links(houses):
    links = [house["link"] for house in houses]
    for i, link in enumerate(links):
        print(f"{i}: {link}")


def plot_xy(x_key, y_key, houses, ax):
    x = [house[x_key] for house in houses]
    y = [house[y_key] for house in houses]
    links = [house["link"] for house in houses]

    ax.scatter(x, y, marker=".")

    # get_summary(x, y)

    ax.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))

    ax.set_title(f'{y_key} vs {x_key} in Rondebosch', fontsize=15)
    ax.set_ylabel(f'{y_key}', fontsize=10)
    ax.set_xlabel(f'{x_key}', fontsize=10)

    for label, x, y in zip(range(len(x)), x, y):
        ax.annotate(label, xy=(x + 0.1, y + 0.1))

    ax.yaxis.set_major_formatter(EngFormatter())


def get_summary(x, y):
    results = sm.OLS(y, sm.add_constant(x)).fit()
    pprint(results.summary())
    print('R2: ', results.rsquared)


def get_property24_houses(url):
    houses = []
    print("Parsing url")
    request = requests.get(URL)

    soup = BeautifulSoup(request.text, features='html.parser')
    print("Processing data from " + url)
    for i, content in enumerate(soup.find_all("div", class_="p24_content")):

        house = {}
        price = content.find_all("div", class_="p24_price")
        description = content.find_all("div", class_="p24_description")
        if price and description:
            if content.parent.has_attr("href"):
                house["link"] = "https://www.property24.com" + content.parent["href"]
            icons = content.find("div", class_="p24_icons")
            attribs = icons.find_all("span")
            for j, attrib in enumerate(attribs):
                if attrib.has_attr("title"):
                    house[attrib["title"].lower()] = attrib.find("span").text

            house["price"] = normalise_from_findall(price)[2:]
            house["description"] = normalise_from_findall(description)
            location = description[0].find_all("span", class_="p24_location")
            house["location"] = normalise_from_findall(location)

            if "bathrooms" in house:
                house["bathrooms"] = format_numbers(house["bathrooms"])
            if "bedrooms" in house:
                house["bedrooms"] = format_numbers(house["bedrooms"])
            if "erf size" in house:
                house["erf size"] = format_numbers(house["erf size"])
            if "floor size" in house:
                house["floor size"] = format_numbers(house["floor size"])
            if "garages" in house:
                house["garages"] = format_numbers(house["garages"])
            if "price" in house:
                house["price"] = format_numbers(house["price"])

        else:
            # print(f"No description found, content:\n{content.prettify()}")
            pass

        for k in house:
            if k not in KEYS:
                KEYS.append(k)
        if len(house) != 0:
            houses.append(house)
    return houses


def format_numbers(s):
    # print(s)
    s = str(s).replace("m²", "").replace(" ", "").strip()
    if s.replace(".", "", 1).isdigit():
        return float(s)
    else:
        raise TypeError(f"{s} is not an integer")


def get_icon_attr(icons, attr):
    attribute = icons.find("span", class_="p24_featureDetails", title=attr)
    if attribute:
        return attribute.find("span").text
    else:
        # print(f"No attr={attr} found, icons:\n{icons.prettify()}")
        return "Unknown"


def normalise_from_findall(s):
    if len(s) != 1:
        raise AssertionError(f"len(price) != 1, len({s}) = {len(s)}")
    return re.sub(RE_NO_BREAK_SPACE, "", s[0].text.strip())


if __name__ == '__main__':
    main()
