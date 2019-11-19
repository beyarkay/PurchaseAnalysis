import datetime
import glob
import os
import re
from pprint import pprint as pprint

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import statsmodels.api as sm
import scipy as sp
from bs4 import BeautifulSoup
from matplotlib import rcParams
from matplotlib.ticker import EngFormatter
from statsmodels.graphics.regressionplots import abline_plot
import seaborn as sns

RE_NO_BREAK_SPACE = re.compile(r"( )")
KEYS = []
NOW = datetime.datetime.now().strftime('%Y_%m_%d')
# COLOURS = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']
COLOURS = ['#db5f57', '#dbc257', '#91db57', '#57db80', '#57d3db', '#5770db', '#a157db', '#db57b2']
URLS = [
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


def main():
    # download_html(URLS)
    # file_paths = sorted(glob.glob(f"_data/{NOW}/*"))
    # extract_and_save_dataframe(file_paths)
    csvs = sorted(glob.glob(f"CSVs/{NOW}/*"))

    plot_csv(csvs[7],
             ["bedrooms", "bathrooms", "garages", "erf size", "floor size"][:3],
             "price")

    # for path in PATHS[:1]:
    #     plot_html(path, saveFig=True)


def download_html(urls):
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
                if "Next" in link.text and "javascript" not in link.get('href') and link.has_attr("data-pagenumber"):
                    # print(f"requests.get({link.get('href')})")
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
        print(f" done; {num_pages} pages from:\t{url}")


def extract_and_save_dataframe(directories):
    for directory in directories:
        print(f"Extracting data from '{directory}'")
        pages = sorted(glob.glob(directory + os.sep + "*"))
        houses = []
        house_id = 0
        for page in pages:
            print(f"\tExtracting data from '{page}'")

            soup = BeautifulSoup(open(page), features='html.parser')
            houses, house_id = extract_houses_from_soup(soup, houses=houses, house_id=house_id)
        # print(f"len(houses)={len(houses)}")
        # print(f"houses='{houses}'")

        df = pd.DataFrame(houses)
        path = f"CSVs/{os.sep.join(directory.split(os.sep)[1:])}.csv"
        directory = os.sep.join(path.split(os.sep)[:-1])
        if not os.path.exists(directory):
            os.makedirs(directory)
        df.to_csv(path, encoding='utf-8')
        # plot_directory(houses, x_keys, y_key, labels)


def extract_houses_from_soup(soup, houses=None, house_id=0):
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
        if len(house) != 0:
            house["id"] = house_id
            house_id += 1
            houses.append(house)
        else:
            # Usually, this means that either the price or description weren't valid
            print(f"\t\tIgnored: https://www.property24.com{house_data.parent['href']}")
    return houses, house_id


def plot_csv(csv_path, x_dims, y_dim, save_figure=False):
    rcParams.update({'figure.autolayout': True,
                     'figure.dpi': 300})
    df = pd.read_csv(csv_path)
    x = df[x_dims]
    y = df[y_dim]

    # make the axes, and plot the data
    fig, axes = plt.subplots(len(x_dims) + 1, figsize=(7, 5 * (len(x_dims) + 1)))
    for i, x_dim in enumerate(x_dims):
        # Add Least Squares Line and r-squared value
        regression_line = df[[x_dim, y_dim]].dropna()
        linreg = sp.stats.linregress(regression_line[x_dim], regression_line[y_dim])

        # First plot the data onto separate axes
        axes[i].plot(regression_line[x_dim],
                     linreg.intercept + linreg.slope * regression_line[x_dim],
                     color=COLOURS[i])
        axes[i].scatter(x[x_dim],
                        y,
                        label=f"{x_dim.title()}, r^2={round(linreg.rvalue ** 2, 2)}",
                        color=COLOURS[i])

        # Then also dump all the data onto the last plot
        axes[-1].plot(regression_line[x_dim],
                      linreg.intercept + linreg.slope * regression_line[x_dim],
                      color=COLOURS[i])
        axes[-1].scatter(x[x_dim],
                         y,
                         label=f"{x_dim.title()}, r^2={round(linreg.rvalue ** 2, 2)}",
                         color=COLOURS[i])

    # add a title and axes labels
    suburb = csv_path.split(os.sep)[-1].split("_")[2].replace("-", " ").title()

    # First plot the data onto separate axes
    for i, x_dim in enumerate(x_dims):
        axes[i].set_xlabel(x_dim.title())
        axes[i].set_ylabel(y_dim.title())
        axes[i].set_title(f"{x_dim.title()} vs {y_dim.title()} \nin {suburb}")

    # Then dump all the data onto the last plot
    x_label = " & ".join([x_dim.title() for x_dim in x_dims])
    axes[-1].set_xlabel(x_label)
    axes[-1].set_ylabel(y_dim.title())
    axes[-1].set_title(f"{x_label} vs {y_dim.title()} \nin {suburb}")

    text = []

    # add a line to connect datapoints from the same house
    for index, row in df.iterrows():
        axes[-1].plot([min(row[x_dims]), max(row[x_dims])],
                      [y[index], y[index]],
                      'k-',
                      alpha=0.3,
                      linewidth=0.25,
                      zorder=1)

        # add the id of each house
        axes[-1].annotate(row["id"],
                          xy=(max(row[x_dims].dropna()) * 1.015, y[index]),
                          size=8,
                          va='center',
                          alpha=0.6)

        text.append(f"{row['id']}: {row['description']}")

    #  # (dont) add an id and link outside of the plot
    # axes[-1].text(1.01, 1.0, "\n".join(text),
    #          ha='left', va='top',
    #          transform=axes[0].transAxes,
    #          size=5)
    # plt.subplots_adjust(right=0.3)

    for ax in axes:
        # add gridlines
        ax.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.7)

        # add ticks and number formatting
        ax.yaxis.set_major_formatter(EngFormatter())
        ax.minorticks_on()
        ax.tick_params(axis='both', which='minor')

        # add legend
        ax.legend(loc='lower right')

    plt.tight_layout()
    plt.show(dpi=800)

    if save_figure:
        path = f"graphs/{os.sep.join(csv_path.split(os.sep)[1:])}"
        directory = os.sep.join(path.split(os.sep)[:-1])

        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(path.replace(".csv", ".png"), dpi=800)


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
