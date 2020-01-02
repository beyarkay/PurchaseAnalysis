# Purchase Analysis

Last Updated: 2020-01-01

PurchaseAnalysis is a general-purpose web scraper 
and visualiser for analysing prices. Currently this 
is applied to housing prices and the second-hand car market

## Usage

### Populating the database
* Running the script `update_cars_db.sh` will:
  * Pull any changes from the github repo
  * Run `project_files/cars/scrape_cars.py` which collects the 
  most up-to-date information about the cars from various websites
  and stores various data about them in `project_files/cars/items.db` 
  and the links to those cars in `project_files/cars/car_links.txt`
  * Push these changes to github in a commit named `Beep Boop: Automatic update from raspberry pi`
* `update_cars_db.sh` is intended to be run from `crontab` automatically
and is set up on a raspberry pi to run every night
* Note that `PurchaseAnalysis/main.py` is deprecated and not in use at all.

### Analysis of the data
* Data analysis isn't automated at the moment, however there are
various cells in `Scratchpad.ipynb` which are usefull for quick graphs of
the data

## Selected Features
* Scrape and parse 20+ variables (engine size, price, number of doors, etc)
from cars.co.za
* Automatically scrape and store the car data every night
* Store the changes in price per vehicle over time

## Example Graphs

### Histogram of cars with & without bluetooth from cars.co.za
![](readme_resources/bt_hist.png)

### Year, Fuel economy, and acceleration of 500 cars from cars.co.za
![](readme_resources/cars_co_za.png)

### Rondebosch Property Prices
![](readme_resources/rondebosch.png)


## File Structure
```
PurchaseAnalysis % tree
.
|-- README.md
|-- Scratchpad.ipynb
|-- Untitled.ipynb
|-- graphs
|   |-- 2019_11_19
|   |   |-- www.property24.com_for-sale_camps-bay_cape-town_western-cape_11014.png
|   |   |-- www.property24.com_for-sale_cape-town-city-centre_cape-town_western-cape_9138.png
|   |   |-- www.property24.com_for-sale_claremont-upper_cape-town_western-cape_14225.png
|   |   |-- www.property24.com_for-sale_claremont_cape-town_western-cape_11741.png
|   |   |-- www.property24.com_for-sale_constantia_cape-town_western-cape_11742.png
|   |   |-- www.property24.com_for-sale_fresnaye_cape-town_western-cape_11016.png
|   |   |-- www.property24.com_for-sale_gardens_cape-town_western-cape_9145.png
|   |   |-- www.property24.com_for-sale_green-point_cape-town_western-cape_11017.png
|   |   |-- www.property24.com_for-sale_muizenberg_cape-town_western-cape_9025.png
|   |   |-- www.property24.com_for-sale_newlands_cape-town_western-cape_8679.png
|   |   |-- www.property24.com_for-sale_observatory_cape-town_western-cape_10157.png
|   |   |-- www.property24.com_for-sale_plumstead_cape-town_western-cape_10094.png
|   |   |-- www.property24.com_for-sale_rondebosch_cape-town_western-cape_8682.png
|   |   |-- www.property24.com_for-sale_sea-point_cape-town_western-cape_11021.png
|   |   `-- www.property24.com_for-sale_woodstock_cape-town_western-cape_10164.png
|   `-- 2019_11_21
|       |-- www.cars.co.za.png
|       `-- www.cars.co.za_best_deals.png
|-- main.py
|-- project_files
|   |-- apartments
|   |   `-- details.md
|   |-- cars
|   |   |-- car_links.txt
|   |   |-- details.md
|   |   |-- graphs
|   |   |-- items.db
|   |   |-- scrape_cars.py
|   |   `-- sql.sql
|   |-- houses
|   |   |-- details.md
|   |   `-- scrape_houses.py
|   `-- template
|       |-- details.md
|       `-- template.csv
|-- readme_resources
|   |-- bt_hist.png
|   |-- cars_co_za.png
|   |-- green_point.png
|   |-- models_vs_price.png
|   |-- models_vs_price_full.png
|   |-- models_vs_price_pruned.png
|   |-- models_vs_price_pruned_cropped.png
|   |-- rondebosch.png
|   |-- sea_point.png
|   `-- woodstock.png
|-- requirements.txt
`-- update_cars_db.sh

```
