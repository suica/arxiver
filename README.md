# arXivER

arXivER is a paper reading assistant using `Flask` and `Vue.js`, which aims at enhancing the experience when using arXiv.

# Install

There are two ways to run arXivER, you can run from source code or choose the way 

from docker. 

## Run from source code

It is recommended that you create virtual environment and activate it first.

If you use anaconda, then you could use this.

`conda create -n arxiver python=3.6`

`conda activate arxiver`

If you don't, you can use your own virtual environment instead, it does not matter.

Now you should install all dependencies, use

`pip install -r requirements.txt`

### Run Main Server

Then go to the project folder.

`python app.py`

to start the server.

Now, arXivER is running on `http://0.0.0.0:5000`.

### Run Celery Worker

`cd async_tasks`

Change `db_address` in `fetch_paper.py` into an absolute address on your computer.

Then run

`sh www.sh`

to execute the celery worker.

## Run from docker

The Dockerfile executes `install.sh` to initial database and install `python3.6`. 

For convinience, we build image included both sqlite and python environment instead of using `docker-compose`.

You can check details in `install.sh` and `Dockerfile`

### How to run

- build image `docker build -t arxiver:0.1`
- run image `docker run -p 5000:5000 -t arxiver:0.1`

Then arXiver is running on `http://127.0.0.1:5000`

## Test

First, run the server first. And run `cd tests`.

Then use `python tests.py` to run the unit tests.

## Deploy

Will be added soon.

## Screen shots

Will be added soon.
