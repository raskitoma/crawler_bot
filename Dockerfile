# Dockerfile
FROM ubuntu:bionic

# setting env vars
ENV DEBIAN_VERSION buster
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONUNBUFFERED=1
ENV PATH "${PATH}:/usr/bin:/opt"
ENV TZ="America/Guayaquil"
ENV tzdata="America/Guayaquil"

# install pre-requisites and etc
RUN apt-get update
RUN DEBIAN_FRONTEND="noninteractive" apt-get -y install tzdata
RUN apt-get install -y \
    python3 \
    python3-pip \
    python3-setuptools \
    software-properties-common \
    wget \
    curl \
    unzip \
    git \
    git-all \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 lsb-release xdg-utils libxss1 libdbus-glib-1-2 \
    xvfb \
    --no-install-recommends -qq

# create path for project store location
RUN mkdir /uploads
RUN mkdir /templates
RUN mkdir /static

# install geckodriver and firefox

RUN GECKODRIVER_VERSION=`curl https://github.com/mozilla/geckodriver/releases/latest | grep -Po 'v[0-9]+.[0-9]+.[0-9]+'` && \
    wget https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz && \
    tar -zxf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

RUN FIREFOX_SETUP=firefox-setup.tar.bz2 && \
    apt-get purge firefox && \
    wget -O $FIREFOX_SETUP "https://download.mozilla.org/?product=firefox-latest&os=linux64" && \
    tar xjf $FIREFOX_SETUP -C /opt/ && \
    ln -s /opt/firefox/firefox /usr/bin/firefox && \
    rm $FIREFOX_SETUP



# adding needed python libraries
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Exposing main ports
EXPOSE 5123

# copy source files
COPY pb_api.py pb_api.py
COPY pb_clickatelly.py pb_clickatelly.py
COPY pb_config.py pb_config.py
COPY pb_crawler.py pb_crawler.py
COPY pb_db.py pb_db.py
COPY pb_gmailer.py pb_gmailer.py
COPY pb_mailer.py pb_mailer.py
COPY pb_string.py pb_string.py
COPY pb_utl.py pb_utl.py
COPY templates/pb_fe.html templates/pb_fe.html
COPY pb_wrapper.sh pb_wrapper.sh
COPY z_items.cfg z_items.cfg
COPY settings.ini settings.ini

# Cleaning image
RUN apt-get autoremove -y

# setting db env var
ENV DATABASE_URI=postgresql://plazabot:plazabot@localhost:5432/plazabot


# setting permissions
RUN ["chmod", "+x", "pb_wrapper.sh"]

# starting services
CMD ./pb_wrapper.sh
