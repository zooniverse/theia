FROM python:3.7-stretch

LABEL maintainer="contact@zooniverse.org"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    postgresql-client \
    gdal-bin \
    libtiff5-dev \
    libgdal-dev \
    python3-gdal \
    binutils \
    netcat \
    libproj-dev \
    libgeoip1 \
    postgis \
  && rm -rf /var/lib/apt/lists/*

RUN pip install pipenv

WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./
COPY start_server.sh ./
COPY start_worker.sh ./

RUN pipenv install --system --dev

RUN export GDAL_VERSION=$(gdal-config --version) \
  && pip install --global-option=build_ext --global-option="-I/usr/include/gdal/" \
    gdal~=${GDAL_VERSION}

COPY . /usr/src/app

# force std in/out to be unbufferred
ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["bash", "start_server.sh"]
