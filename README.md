# Prizebond Draw
# Project Description
Prize Bond Draw is a web application for managing prize bonds which are a unique method of investment that are essentially lotteries backed by the government.

1. This is a full stack web application that supports all the CRUD operations.
2. Supports role based mechanism to authorize the users.
    - `Admin` Can add denominations and their respective prizes, update the winning list and annouce the notifications to all the users.
    - `User` Can store their bond serials and check the results of either all of their serials or by entering any particular serial.
3. One unique feature is that you can add your bond serial by just uploading their picture.

If you would like to read more about how prize bond works then check out this link [Prize Bond](https://profit.pakistantoday.com.pk/2021/08/01/all-you-need-to-know-about-government-prize-bonds/).

>NOTE: I have made this website in accordance with how the prize bond works in Pakistan only and I am not sure of the process followed in other countries.

# Tech Stack
Here's the breif overview of the tech stack I have used:

* This project uses [Flask Microframework](https://flask.palletsprojects.com/en/2.0.x/). Flask is a open source python web framework that is built with only minimalistic features and easy to extend philosophy.

* For data storage the project uses [Postgresql](https://www.postgresql.org/) which is an open source relational database.

* Various other flask extension have been used to further extend the functionalities as flask only provides the core features.

* For the User Interface the project uses [HTML/CSS](https://www.w3.org/standards/webdesign/htmlcss) , [Javascript](https://developer.mozilla.org/en-US/docs/Web/JavaScript) and [Bootstrap V5.0](https://getbootstrap.com/docs/5.0/getting-started/introduction/).

* For the extraction of serial and denomination from the bond picture, the project uses Microsoft Azure [Optical Character Recognition](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/overview-ocr) service.

# Installation Instructions For Ubuntu 20.04 LTS
## Database Setup
1. Install Postgresql on Ubuntu.
 ``` 
 sudo apt update
 sudo apt install postgresql postgresql-contrib
 ```
 2. Access the postgres prompt by running.
 ```
 sudo -u postgres psql
 ```
 3. Create a new database and the user.
 ```
 CREATE DATABASE prizebond_draw_db;
 CREATE USER prizebond_draw_user WITH PASSWORD 'password';
 ```
 4. Now grant the access rights to our newly created database user.
 ```
 GRANT ALL PRIVILEGES ON DATABASE prizebond_draw_db TO prizebond_draw_user;
 ``` 
 5. Now exit the shell.
 ```
 /q
 ```
## Getting the Project Dependencies

Make sure you have python3 and pip3 installed.

1. Clone the repository and navigate to the project directory.
```
git clone https://github.com/zain2323/prizebond-draw.git
cd prizebond-draw
```
2. Activate the virtual environment.
```
source venv/bin/activate
```
3. Install this package first as it is a required dependency for psycopg2 library.
```
sudo apt install python3-dev libpq-dev
```
4. Now install all the required dependencies.
```
pip3 install -r requirements.txt
```

## Obtaining Azure Subscription_Key and Endpoint
1. Create [Microsoft Azure](https://azure.microsoft.com/en-us/) account if you don't have one.
2. To obtain `subscription_key` and `endpoint` refer to this [official guide](https://docs.microsoft.com/en-us/azure/cognitive-services/computer-vision/quickstarts-sdk/client-library?tabs=visual-studio&pivots=programming-language-python). 
## Setting Up the Application Configurations
1. navigate to the project directory.
```
cd prizebond-draw
```
2. Copy the ```secrets.json``` file to the ```/etc/``` directory.
```
sudo cp secrets.json /etc/
```
3. To generate a secret key for the project run this script in the python shell and copy the output string.
```python
import secrets
secrets.token_hex()
```
4. Now open the secrets.json file.
```
sudo nano /etc/secrets.json
```
5. Replace all the necessary details in the file with the correct one.
```JSON
{
    "SECRET_KEY": "<PASTE YOUR SECRET KEY HERE>",
    "MAIL_USERNAME":"<USERNAME>",
    "MAIL_PASSWORD": "<PASSWORD>",
    "EMAIL": "<EMAIL>",
    "DB_PASSWORD": "<DB_PASSWORD>",
    "DB_ROLE": "<DB_ADMIN>",
    "DB_NAME": "<DB_NAME>",
    "HOST": "<DB_SERVER>",
    "SUBSCRIPTION_KEY": "<YOUR MICROSOFT AZURE SUBSCRIPTION_KEY>",
    "ENDPOINT": "<YOUR MICROSOFT AZURE ENDPOINT>"
}
```
6. Make sure to save all the changes.

>If you are running this application locally then `"HOST": "localhost" `

## Running the Application
1. Initialize the flask environment variable and run the migration script.
```
export FLASK_APP=run.py
flask db upgrade
```
2. To run the application execute this command.
```
flask run
```
 Now navigate to the [localhost](localhost:5000) to use the application.

# Copyright
This project is distributed under the [MIT License](https://github.com/zain2323/prizebond-draw/blob/main/LICENSE).
