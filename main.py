from bs4 import BeautifulSoup
import requests
import re
from pprint import pprint as pprint

URL = "https://www.property24.com/for-sale/rondebosch/cape-town/western-cape/8682"
RE_NO_BREAK_SPACE = re.compile(r"( )")


def main():
    house = {}

    request = requests.get(URL)
    soup = BeautifulSoup(request.text, features='html.parser')

    for i, content in enumerate(soup.find_all("div", class_="p24_content")[:50]):
        # item = item.text.replace("\n", "")
        price = content.find_all("div", class_="p24_price")
        description = content.find_all("div", class_="p24_description")
        if description:

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
            print(f"No description found, content:\n{content.prettify()}")
            # pass

        pprint(house)
        print()


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
