FROM python:3

LABEL maintainer="contact@zooniverse.org"

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    postgresql-client \
    gdal-bin \
    libtiff5-dev \
    libgdal-dev \
    python-gdal \
    python3-gdal \
    binutils \
    netcat \
    libproj-dev \
    libgeoip1 \
    postgis \
  && rm -rf /var/lib/apt/lists/*

RUN pip install \
  pipenv

WORKDIR /usr/src/app

COPY Pipfile ./
COPY Pipfile.lock ./
COPY start_server.sh ./
COPY start_worker.sh ./

RUN pipenv install --system --dev

# libtiff doesn't work correctly under linux because the debian packages are out of date
# so just uninstall the package and re-add it from github
RUN pip uninstall --yes libtiff
RUN pip install -e git+https://github.com/pearu/pylibtiff#egg=libtiff

RUN export GDAL_VERSION=$(gdal-config --version) \
  && pip install --global-option=build_ext --global-option="-I/usr/include/gdal/" \
    gdal~=${GDAL_VERSION}

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["bash", "start_server.sh"]
