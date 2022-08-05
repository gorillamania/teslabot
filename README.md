# TeslaBot 🤖

Automating functionality for Tesla, using the unnoffical API + via (Tessie)[https://tessie.com/]

## Auto Venting
It's hot out. Sun is streaming in. Interior temperatures can exceed 100°F, damaging the cars interior and making it uncomfortable when you get in. Tesla has a feature to cool down the cabin when it gets hot, but this uses up battery.

Yes, you can open the app to vent, but it's not ideal to have to remember to do it every time you park. It's also nice to only vent the windows when it is hot, not all the time.

autovent solves this by allowing you to set a threshold for venting

`python autovent.py --help`


## Off peak charging

Tesla's native off-peak scheduling sucks. It allows you to specify a "start time", but no end time, when in practicality you need to be able to specify a peak window, such as 4-9PM for PG&E in Northern California, and have the charging stop during this window


`python peakoff.py --help` 
