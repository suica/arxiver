# arXivER

arXivER is a paper recorder which aims at enhancing the experience when using arXiv.

## Run

It is recommended that you create virtual environment and activate it first.

If you use anaconda, then you could use this.

`conda create -n arxiver python=3.6`

`conda activate arxiver`

If you don't, you can use your own virtual environment instead, it does not matter.

Now you should install all dependencies, use

`cd app`

`pip install -r requirements.txt`

### Run Main Server


Then go to the project folder.

`python app.py`

to start the server.

Now, arXivER is run on `http://0.0.0.0:5000`.


### Run Celery Worker

`cd app/async_tasks`

Change `db_address` in `fetch_paper.py` into an absolute address on your computer.

Then run

`sh www.sh`

to execute the celery worker.

## Test

First, run the server first. And run `cd app/tests`.

Then use `python tests.py` to run the unit tests.
