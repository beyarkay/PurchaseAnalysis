#!/bin/bash
dt=$(date '+%d-%m-%Y %H:%M:%S')

echo "=====================$dt====================="
cd ~/git_repos/PurchaseAnalysis
source venv/bin/activate
psql items
\o log.txt
SELECT date, COUNT(*) FROM dates_cars GROUP BY date ORDER BY date;
\o
\q
echo "-----------DONE------------"
deactivate
