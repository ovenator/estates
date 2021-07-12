FROM python:3.8

RUN pip install 'pipenv==2018.11.26'

COPY Pipfile /app/
COPY Pipfile.lock /app/
WORKDIR /app

# install, fail if Pipfile.lock is out of date
ENV PIPENV_VENV_IN_PROJECT=1
RUN pipenv install --deploy

COPY . /app