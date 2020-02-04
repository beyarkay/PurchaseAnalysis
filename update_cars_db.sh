#!/bin/bash
dt=$(date '+%d-%m-%Y %H:%M:%S')

if [ "$1" == "0" ]; then
  echo "=====================$dt====================="
  cd ~/git_repos/PurchaseAnalysis
  source venv/bin/activate
  echo "-----------PULLING FROM REPO-----------"
  git add .
  git commit -m "Beep Boop: Pre-commit before rebase"
  git pull --rebase
  echo "-----------EXECUTING SCRIPT------------"
  python3 -u ~/git_repos/PurchaseAnalysis/project_files/cars/scrape_cars.py "$1" "$2"
  git add .
  git commit -m "Beep Boop: Automatic update from raspberry pi"
  echo "-----------PUSHING TO REPO-------------"
  git pull --rebase
  git push -u origin master
else
  cd ~/git_repos/PurchaseAnalysis
  source venv/bin/activate
  git add . >/dev/null
  git commit -m "Beep Boop: Pre-commit before rebase" >/dev/null
  git pull --rebase >/dev/null
  python3 -u ~/git_repos/PurchaseAnalysis/project_files/cars/scrape_cars.py >/dev/null
  git add . >/dev/null
  git commit -m "Beep Boop: Automatic update from raspberry pi" >/dev/null
  git pull --rebase >/dev/null
  git push -u origin master >/dev/null
fi

deactivate
