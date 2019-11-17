import datetime
import os
import re
from pprint import pprint as pprint
import glob
import matplotlib.pyplot as plt
import numpy as np
import requests
import statsmodels.api as sm
from bs4 import BeautifulSoup
from matplotlib import rcParams
from matplotlib.ticker import EngFormatter

RE_NO_BREAK_SPACE = re.compile(r"( )")
KEYS = []
PATHS = [
    "_data/claremont-2019_10_26.html",
    "_data/mowbray-2019_10_26.html",
    "_data/newlands-2019_10_26.html",
    "_data/rondebosch-2019_10_26.html"
]

URLS = [
    "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682",
    "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682/p2",
    "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682/p3",
    "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682/p4",
    "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682/p5",
    "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682/p6"
]


def main():
    global PATHS
    download_html(URLS)
    PATHS = sorted(glob.glob("_data/*"))
    for path in PATHS:
        plot_html(path, saveFig=True)


def plot_html(path, saveFig=False, normalise=True):
    houses = get_p24_houses(path)

    x_keys = [
        "bedrooms",
        "bathrooms",
        "garages",
        "erf size",
        "floor size"
    ]
    y_key = "price"

    fig, ax = plt.subplots(figsize=(8, 14))

    xlabel = "\n & ".join([x_key.capitalize() for x_key in x_keys])
    ylabel = y_key.capitalize()

    for x_key in x_keys:
        plot_xy(x_key, y_key, houses, ax, normalise=normalise)
    ax.set_title(f'{ylabel} vs \n({xlabel}) \nin {path.split(os.sep)[1]}',
                 fontsize=15)

    ax.set_ylabel(f'{ylabel}', fontsize=10)
    ax.set_xlabel(f'{xlabel}', fontsize=10)

    ax.yaxis.set_major_formatter(EngFormatter())
    ax.minorticks_on()
    ax.tick_params(axis='x', which='minor', bottom=False)

    ax.grid(True)
    ax.legend(loc='lower right')
    rcParams.update({'figure.autolayout': True})
    if saveFig:
        write_path = "graphs/" + path.split(os.sep)[1]
        plt.savefig(write_path.replace(".html", ".png"))
        with open(write_path.replace(".html", ".txt"), "w+") as write_file:
            write_file.write("\n".join([f"{i}: {link}" for i, link in get_links(houses, should_print=False)]))
    else:
        plt.show()
        get_links(houses)


def plot_xy(x_key, y_key, houses, ax, normalise=True):
    x = []
    y = []
    labels = []

    for house in houses:
        if x_key in house and house[x_key] is not None:
            x.append(house[x_key])
            y.append(house[y_key])
            labels.append(house["id"])

    x_norm = []
    if normalise:
        for x_val in x:
            max_x = max([i for i in x if i is not None])
            min_x = min([i for i in x if i is not None])
            x_norm.append((x_val - min_x) / max(max_x - min_x, 1))
    else:
        x_norm = x
    ax.scatter(x_norm, y, marker=".", label=x_key.capitalize())

    for label, x_i, y_i in zip(labels, x_norm, y):
        ax.annotate(label, xy=(x_i, y_i))

    if len(x_norm) > 5:
        ax.plot(np.unique(x_norm),
                np.poly1d(np.polyfit(x_norm, y, 1))(np.unique(x_norm)))
    else:
        print("Not enough data to plot Least Squares Line: " + x_key)


def get_links(houses, should_print=True):
    links = [(house["id"], house["link"]) for house in houses]
    links.sort(key=lambda x: x[0])
    if should_print:
        for id, link in links:
            print(f"{id}: {link}")
    else:
        return links


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


def get_p24_houses(url_path):
    houses = []

    if os.path.exists(url_path):
        print(f"Opening filepath: {url_path}")
        soup = BeautifulSoup(open(url_path), features='html.parser')
    else:
        print(f"Parsing url: {url_path}")
        request = requests.get(url_path)
        soup = BeautifulSoup(request.text, features='html.parser')

    print("Processing data from " + url_path)
    count = 0
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
            else:
                house["floor size"] = None
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
            house["id"] = count
            count += 1
            houses.append(house)
    return houses


def format_numbers(s):
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
        return "Unknown"


def normalise_from_findall(s):
    if len(s) != 1:
        raise AssertionError(f"len(price) != 1, len({s}) = {len(s)}")
    return re.sub(RE_NO_BREAK_SPACE, "", s[0].text.strip())


if __name__ == '__main__':
    main()
