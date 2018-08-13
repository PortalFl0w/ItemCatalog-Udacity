# Furniture Catalog - Furnita - Udacity Project

##Description
A fictional furniture store made for a Udacity Full Stack Web Development project.

## Prerequisites

You need to download and install this software before running this project.

* [VirtualBox](https://www.virtualbox.org/wiki/Downloads) - Virtual Machine Software
* [Vagrant](https://www.vagrantup.com/downloads.html) - Allows you to work on your local files from within the virtual machine.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Google API
**IMPORTANT** In order to run this application you will need to generate some credentials for the Google API using your google account. Please follow the steps:

1. [Follow this to generate credentials](https://developers.google.com/adwords/api/docs/guides/authentication#webapp)
2. Download the JSON file provided on the same page as the list of your app credentials.
3. Put the file into the same directory as this repo and name it ```client_secrets.json```

### Installing

1. Install Prerequisites
2. Clone This Repository
3. Create Google Credentials file. (See **Google API** section of readme)
4. Run ```vagrant up``` and ```vagrant ssh``` to start up and access the virtual machine. Once in, navigate to the project folder ```cd /vagrant```
5. Run ```python setup.py```
6. (Optional) Run ```python dummy.py``` to import dummy data into the database.
7. Run ```python project.py``` and go to ```http://localhost:5000``` to access the application.

## Default JSON API Endpoints

URI: ```/category/<int:category_id>/item/JSON```  
Shows all items inside a category

URI: ```/category/<int:category_id>/item/<int:item_id>/JSON```  
Show information about a single item

URI: ```/category/JSON```  
Shows a list of categories

## Features
- User Authorization system using Google OAuth2.0
- Cross-site Request Forgery protection

## Built With

* [Python](https://www.python.org/downloads/release/python-370/) - Programming language used
* [SQLite](https://www.sqlite.org/index.html) - SQL Database

## Authors

* **Mateusz Lipski** - *Initial work* - [PortalFl0w](https://github.com/PortalFl0w)
