FROM python:3

LABEL maintainer="contact@zooniverse.org"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    postgresql-client \
    gdal-bin \
    libgdal-dev \
    python3-gdal
  # && rm -rf /var/lib/apt/lists/*

RUN pip install \
  pipenv

WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./

RUN pipenv install --system --deploy

RUN export GDAL_VERSION=$(gdal-config --version) \
  && pip install --global-option=build_ext --global-option="-I/usr/include/gdal/" \
    gdal~=${GDAL_VERSION}

CMD ["sleep", "infinity"]

# COPY . .

EXPOSE 80
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]