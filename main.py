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
            icons = content.find("div", class_="p24_icons")
            attribs = icons.find_all("span")
            for j, attrib in enumerate(attribs):
                if attrib.has_attr("title"):
                    house[attrib["title"].lower()] = attrib.find("span").text

            # house["bedrooms"] = get_icon_attr(icons, "Bedrooms")
            # house["bathrooms"] = get_icon_attr(icons, "Bathrooms")
            # house["garages"] = get_icon_attr(icons, "Garages")
            # house["sq_meters"] = get_icon_attr(icons, "Floor Size")

            house["price"] = int(normalise_from_findall(price)[2:])
            house["description"] = normalise_from_findall(description)
            location = description[0].find_all("span", class_="p24_location")
            house["location"] = normalise_from_findall(location)
        else:
            # print(f"No description found, content:\n{content.prettify()}")
            pass

        pprint(house)
        print()


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
