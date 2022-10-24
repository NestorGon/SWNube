# start by pulling the python image
FROM python:3

# switch working directory
WORKDIR /app

# copy every content from the local file to the image
COPY . /app

# activate virtual environment
RUN . bin/activate

# install the dependencies and packages in the requirements file
RUN pip install -r requirements.txt

CMD cd flaskr/; flask run -h 0.0.0.0 & cd batch_process; celery -A batch worker -l info