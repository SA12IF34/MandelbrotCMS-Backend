<h1 align="center">MandelbrotCMS Backend</h1>

[Live Production](https://cms.saifchan.site/)
<hr>

## About the Project
The Backend of MandelbrotCMS project, the project is built using Django with scalability and reliabilty in mind.

Each app represents an individual part of MandelbrotCMS system, and made the database design to be adaptable to microservices architecture.

### The project includes the following apps
* Authentication: Responsible for handling user authentication, profile and settings actions in The Central
* Missions: Responsible for handling mission lists, creation, connectig to other parts, tracking, updating and deletion
* Sessions Manager: Responsible for handling projects creation, updating, and deleting
* Learning Tracker: Responsible for handling retrieving user's courses data with web scraping and APIs, creating course objects and applying CRUD operations on them
* Entertainment: Responsible for handling creating material objects and serving different APIs for various tasks
* Goals: Responsible for creating, reading, updating and deleting goal objects, with the ability to connect differnt object records from different parts to the goal objects
* Parent: Contains code snippets and objects shared through most the apps or all of them

## How to Run Locally
### Prerequisits
To be able to running it locally, you must have:
* Python installed on your machine

### Best practices
We recommend you to install project requirements in a [virtual environment](https://docs.python.org/3/library/venv.html#creating-virtual-environments)

### Installation and Configuration
#### Installation
To install the required libraries and modules for the project run the following command in project's root directory:
```
pip install -r requirements.txt
```

#### Configuration:
Before running the project, you must create a .env file in project's root directory that contains the following keys:
```.env
SECRET_KEY="Django secrect Key"
JWT_ALGORITHM="JWT signing algorithm (e.g HS256)"
YOUTUBE_API_KEY="Youtube API Key"
MAL_CLIENT_ID="Myanimelist API client ID"
MAL_CLIENT_SECRET="Myanimelist API client secret"
GOOGLE_CLIENT_SECRET="Google client secret for social authentication"
GOOGLE_CLIENT_ID="Google client id for social authentication"
GITHUB_CLIENT_ID="Github client id for social authentication"
GITHUB_CLIENT_SECRET="Github client secret for social authentication"
```
To make sure MAL API runs, you must retrieve access and refresh tokens for the API, 
and store them in a json file in entertainment app called `tokens.json`

To enable Database tables run the following commands in project's root directory:
```
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### Running the project
To start the project, run:
```
python manage.py runserver
```
It will run on the local host with 10000 port

## Contribution
Feel free to fork the repository and creating pull requests

<hr>
This was the repository for the Backend of MandelbrotCMS.

[The repo for the Frontend](https://github.com/SA12IF34/MandelbrotCMS-Frontend)
