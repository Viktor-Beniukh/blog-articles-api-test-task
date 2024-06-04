# Blog Articles API

API service for blog management with the ability to obtain articles from a site by scraping them


### Installing using GitHub

- Python3 must be already installed
- Install PostgreSQL and create db
- Chromedriver must be already installed (or another driver for your browser)

```shell
git clone https://github.com/Viktor-Beniukh/blog-articles-api-test-task.git
cd blog-articles-api-test-task
python3 -m venv venv
source venv/bin/activate (for Linux or macOS) or venv\Scripts\activate (for Windows)
pip install poetry
poetry install
python manage.py migrate
python manage.py runserver   
```

You need to create directory `media` and `static`

You need to create `.env.prod` file and add there the variables with your according values 
to run the project into docker (e.g. `.env.prod.sample`):
- `POSTGRES_DB`: this is databases name;
- `POSTGRES_USER`: this is username for databases;
- `POSTGRES_PASSWORD`: this is username password for databases;
- `POSTGRES_HOST`: this is host name for databases;
- `POSTGRES_PORT`: this is port for databases;
- `SECRET_KEY`: this is Django Secret Key - by default is set automatically when you create a Django project.
                You can generate a new key, if you want, by following the link: `https://djecrety.ir`;
- `DJANGO_DEBUG=False`;

- `EMAIL_HOST_USER`: this is email of sender, created on smtp server;
- `EMAIL_HOST_PASSWORD`: this is password of application, created on smtp server;
- `DEFAULT_FROM_EMAIL`: this is email of sender;
- `EMAIL_PORT`: this is port of smtp server;
- `EMAIL_HOST`: this is smtp server;

- `BOT_TOKEN`: your token received when creating the Telegram bot;
- `TELEGRAM_CHAT_ID`: chat_id received when creating the Telegram bot;

- `CELERY_BROKER_URL` & `CELERY_RESULT_BACKEND`: they're used to create periodic tasks. Have to install Celery & Redis;


To check functionality of the project without docker, you need to create `.env` file and add there the variables 
with your according values (e.g. `.env.sample`):
- `SECRET_KEY`: this is Django Secret Key - by default is set automatically when you create a Django project.
                You can generate a new key, if you want, by following the link: `https://djecrety.ir`;
- `DJANGO_DEBUG=True`;

- `EMAIL_HOST_USER`: this is email of sender, created on smtp server;
- `EMAIL_HOST_PASSWORD`: this is password of application, created on smtp server;
- `DEFAULT_FROM_EMAIL`: this is email of sender;
- `EMAIL_PORT`: this is port of smtp server;
- `EMAIL_HOST`: this is smtp server;

- `BOT_TOKEN`: your token received when creating the Telegram bot;
- `TELEGRAM_CHAT_ID`: chat_id received when creating the Telegram bot;

Optional: you can add a variable called `LOG_LEVEL` to `.env` and `.env.prod` files, if you want to change a level of logging


# Warning! It's important!
You need to add to core of the project chromedriver file for scraping! Driver version must match browser version!
Here's the link to download it: `https://developer.chrome.com/docs/chromedriver/downloads`


## Run with docker

Docker should be installed

- Create docker image: `docker-compose build`
- Run docker app: `docker-compose up` or `docker-compose up -d` (to work in this terminal)
- Create schedule for running sync in DB (django-celery-beat is used to set the periodicity of tasks via admin panel.)



## Getting access

- Create user via /auth/users/register/
- Get token authentication via /auth/users/login/
- Logout and delete token authentication via /auth/users/logout/


## Features

- Token authentication;
- Admin panel /admin/;
- Documentation is located at /api/v1/doc/swagger/;
- Creating, reading, updating and deleting articles by current user (only authenticated user);
- Filtering articles by title and scraped_title (only authenticated user);


### How to create superuser
- Run `docker-compose up` command, and check with `docker ps`, that all services are up and running;
- Create new admin user. Enter container `docker exec -it <container_name> bash`, and create in from there (web image);


### What do APIs do

- [GET] /api/v1/blog/articles/ - obtains a list of articles with the possibility of filtering by title;
- [GET] /api/v1/blog/scraped_articles/ - obtains a list of scraped_articles with the possibility of filtering by scraped_title;
- [GET] /api/v1/blog/articles/id/ - obtains the specific article information data;
- [GET] /api/v1/blog/scraped_articles/id/ - obtains the specific scraped article information data;

- [POST] /api/v1/blog/articles/ - creates an article;
- [POST] /api/v1/blog/articles/id/upload-picture/ - uploads an article picture (by author of the article);

- [PUT] /api/v1/blog/articles/id/ - updates the article data (only author of the article);

- [PATCH] /api/v1/blog/articles/id/ - partial updates the article data (only author of the article);

- [DELETE] /api/v1/blog/articles/id/ - deletes the article data (only author of the article);


- [GET] /auth/users/me/ - obtains the specific user information data;

- [POST] /auth/users/register/ - creates new users;
- [POST] /auth/users/login/ - creates token authentication for user;
- [POST] /auth/users/logout/ - log out user and delete token authentication;
- [POST] /auth/users/me/profile-create/ - creates user profile (upload image);

- [PUT] /auth/users/me/id/profile-update/ - updates user profile (upload image);
- [PATCH] /auth/users/me/ - updates the specific user information data;

- [POST] /auth/users/password/reset/request/ - sending message to user email for updating password;
- [PUT] /auth/users/password/reset/confirm/uidb64/token/ - set up new user password;


### Checking the endpoints functionality
- You can see detailed APIs at swagger page: `http://127.0.0.1:8000/api/v1/doc/swagger/`.


## Testing

- Run tests using different approach: `docker-compose run app sh -c "python manage.py test"`.


## Check project functionality

Superuser credentials for test the functionality of this project:
- email address: `migrated@admin.com`;
- password: `migratedpassword`.


### Commands for manual running of tasks

- locally: `python manage.py scrape_articles` - run scraper;
- locally: `python manage.py import_articles` - add articles to database after scraping;
- locally: `python manage.py article_telegram_bot` - run telegram bot;

- docker: `docker exec -it <container_name> python manage.py scrape_articles` - run scraper;
- docker: `docker exec -it <container_name> python manage.py import_articles` - add articles to database after scraping;
