FROM python:3

LABEL maintainer="contact@zooniverse.org"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    postgresql-client \
    gdal-bin \
  && rm -rf /var/lib/apt/lists/*
  # https://gist.github.com/cspanring/5680334 for gdal-bin

RUN pip install \
  && pipenv

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pipenv install --system --deploy

COPY . .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]