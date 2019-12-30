#!/bin/bash

cd ~/git_repos/PurchaseAnalysis
git pull
python3 -u ~/git_repos/PurchaseAnalysis/project_files/cars/scrape_cars.py
git add .
git commit -m "Automatic update to cars.csv"
git push -u origin master
