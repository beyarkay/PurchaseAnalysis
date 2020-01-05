#!/bin/bash

dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "=====================$dt====================="
ip route
cd ~/git_repos/PurchaseAnalysis
source venv/bin/activate
echo "-----------PULLING FROM REPO-----------"
git add .
git commit -m "Beep Boop: Pre-commit before rebase"
git pull --rebase
echo "-----------UPDATING REQUIREMENTS-----------"
pip install -r requirements.txt
echo "-----------EXECUTING SCRIPT------------"
python3 -u ~/git_repos/PurchaseAnalysis/project_files/cars/scrape_cars.py
git add .
git commit -m "Beep Boop: Automatic update from raspberry pi"
echo "-----------PUSHING TO REPO-------------"
git push -u origin master
deactivate
