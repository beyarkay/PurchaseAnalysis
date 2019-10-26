import os

from bs4 import BeautifulSoup
import requests
import datetime
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
    urls = [
        "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682",
        "https://www.property24.com/for-sale/mowbray/cape-town/western-cape/8677",
        "https://www.property24.com/for-sale/claremont/cape-town/western-cape/11741",
        "https://www.property24.com/for-sale/newlands/cape-town/western-cape/8679"
    ]
    download_html(urls)
    pass
    houses = get_property24_houses(URL)
    houses.sort(key=lambda x: x["price"])
    print(KEYS)

    x_keys = [
        "bedrooms",
        "bathrooms",
        "garages",
        "erf size"
        # "floor size",
    ]
    y_key = "price"

    fig, ax = plt.subplots(figsize=(8, 8))

    for x_key in x_keys:
        plot_xy(x_key, y_key, houses, ax)
    ax.set_title(f'{y_key} vs ({" & ".join([x_key for x_key in x_keys])}) in Rondebosch',
                 fontsize=15)

    ax.set_ylabel(f'{y_key.capitalize()}', fontsize=10)
    ax.set_xlabel(f'{" & ".join([x_key for x_key in x_keys])}', fontsize=10)

    ax.yaxis.set_major_formatter(EngFormatter())
    ax.tick_params(axis='y',
                   which='minor',
                   direction='out',
                   bottom=True,
                   length=5)

    plt.grid(True)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.show()
    print_links(houses)


def plot_xy(x_key, y_key, houses, ax):
    x = []
    y = []
    for house in houses:
        if x_key in house:
            x.append(house[x_key])
        else:
            x.append(0)
        y.append(house[y_key])

    x_norm = [(x_val - min(x)) / (max(x) - min(x)) for x_val in x]

    ax.scatter(x_norm, y, marker=".")

    ax.plot(np.unique(x_norm),
            np.poly1d(np.polyfit(x_norm, y, 1))(np.unique(x_norm)),
            label=x_key.capitalize())

    for label, x, y in zip(range(len(x_norm)), x_norm, y):
        ax.annotate(label, xy=(x, y))


def print_links(houses):
    links = [house["link"] for house in houses]
    for i, link in enumerate(links):
        print(f"{i}: {link}")


def get_summary(x, y):
    results = sm.OLS(y, sm.add_constant(x)).fit()
    pprint(results.summary())
    print('R2: ', results.rsquared)


def download_html(urls):
    for url in urls:
        now = datetime.datetime.now().strftime('%Y_%m_%d')
        path = f"_data/{url.split('/')[4]}-{now}.html"
        print(f"requests.get({url})")
        request = requests.get(url)

        with open(path, "w+") as write_file:
            write_file.write(request.text)


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
