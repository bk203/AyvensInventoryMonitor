# Ayvens Inventory Monitor

Application to monitor inventory of Ayvens products, to keep track of the stock and sales of the products. This
application is built using Python.

This is a personal project that I am working on to keep track of the inventory for selecting a used lease car. The stock
goes fast so these notifications help me get there first.

Application fetches all cars from the Ayvens website that comply to the 'zo goed als nieuw' and 'occasion' filters.
After the first inital fetch is stored to file each subsequent fetch will compare the new fetch with the previous fetch
and notify the user of any new cars that have been added to the inventory.

I oped to use a Telegram bot to send the notifications to the user.

## Running the application using Docker
1. perpare the .env file, create a local copy or rename the .env.example file to .env and fill in the required values
2. Run the following command to build the docker image
```shell
docker-compose --env-file .env.example up
```
3. The application will start and run in the background until the fetch is complete. The application will then notify the user of changes and shutdown.

For repeated use, use a cronjob to run the application at a set interval.