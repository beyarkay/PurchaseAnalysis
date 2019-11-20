# Purchase Analysis

PurchaseAnalysis scrapes property prices and various other data points from 
popular real estate websites, and then visualises the data in order to better 
spot outliers that are under- or over-priced.

## Usage

* The `main()` method in `main.py` looks like so:
```
def main():
    download_html(URLS)
    file_paths = sorted(glob.glob(f"_data/{NOW}/*"))
    extract_and_save_dataframe(file_paths)
    csvs = sorted(glob.glob(f"CSVs/{NOW}/*"))

    for csv in csvs:
        plot_csv(csv,
                 ["bedrooms", "bathrooms", "garages", "erf size", "floor size"],
                 "price", save_figure=True)
```

* `download_html(URLS)` will download each of the urls specified in the `URLS` list
* `extract_and_save_dataframe(file_paths)` will save the data found in the property24 html files `file_paths` as `.csv` files
* `plot_csv(csv_path, x_dims, y_dim, save_figure=False):` will create plots with the x_dims and y_dim specified, from the single `csv_path`
* Example plots are shown below

## Example Graphs

### Newlands Property Prices
![](readme_resources/newlands.png)

### Green Point Property Prices
![](readme_resources/green_point.png)

### Rondebosch Property Prices
![](readme_resources/rondebosch.png)

### Sea Point Property Prices
![](readme_resources/sea_point.png)

### Woodstock Property Prices
![](readme_resources/woodstock.png)


## Current Features

* Automatically navigates to the following pages of search results and add it all as one dataset
* r-squared values for the linear regression lines to indicate their goodness-of-fit

## Future Features to Add

* Include the number of datapoints plotted
* Don't display a graph if there weren't enough data points to plot?
* Make the graphs more intuitive to get an understanding of
* Add ability to see trends in a suburb over time
* increase granularity in search parameters: add ability to graph search results based 
off of different parameters

## File Structure
```
PurchaseAnalysis % tree -L 2

.
├── CSVs
│   └── 2019_11_19
├── README.md
├── _data
│   └── 2019_11_19
├── graphs
│   └── 2019_11_19
├── main.py
├── readme_resources
│   ├── green_point.png
│   ├── newlands.png
│   ├── rondebosch.png
│   ├── sea_point.png
│   └── woodstock.png
└── requirements.txt
```