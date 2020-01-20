#!/bin/bash

dt=$(date '+%d/%m/%Y %H:%M:%S');
echo "=====================$dt====================="
cd ~/git_repos/PurchaseAnalysis
source venv/bin/activate
echo "-----------PULLING FROM REPO-----------"
git add . > /dev/null
git commit -m "Beep Boop: Pre-commit before rebase" > /dev/null
git pull --rebase > /dev/null
#echo "-----------UPDATING REQUIREMENTS-----------"
#pip install -r requirements.txt
echo "-----------EXECUTING SCRIPT------------"
python3 -u ~/git_repos/PurchaseAnalysis/project_files/cars/scrape_cars.py
git add . > /dev/null
git commit -m "Beep Boop: Automatic update from raspberry pi" > /dev/null
echo "-----------PUSHING TO REPO-------------"
git pull --rebase > /dev/null
git push -u origin master > /dev/null
deactivate
