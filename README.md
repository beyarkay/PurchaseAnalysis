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
