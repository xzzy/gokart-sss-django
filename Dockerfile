# Prepare the base environment.
FROM ubuntu:22.04 as builder_base_govapp
MAINTAINER asi@dbca.wa.gov.au

ENV DEBIAN_FRONTEND=noninteractive
#ENV DEBUG=True
ENV TZ=Australia/Perth
ENV DEFAULT_FROM_EMAIL='no-reply@dbca.wa.gov.au'
ENV NOTIFICATION_EMAIL='no-reply@dbca.wa.gov.au'
ENV NON_PROD_EMAIL='none@none.com'
ENV PRODUCTION_EMAIL=False
ENV EMAIL_INSTANCE='DEV'
ENV SECRET_KEY="ThisisNotRealKey"
ENV SITE_DOMAIN='dbca.wa.gov.au'


RUN apt-get clean
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y curl wget git libmagic-dev gcc binutils libproj-dev gdal-bin python3 python3-setuptools python3-dev python3-pip tzdata cron rsyslog gunicorn
RUN apt-get install --no-install-recommends -y libpq-dev patch libreoffice virtualenv 
RUN apt-get install --no-install-recommends -y postgresql-client mtr htop vim  sudo
RUN apt-get install --no-install-recommends -y bzip2 pdftk
RUN apt-get install --no-install-recommends -y libgdal-dev build-essential
RUN ln -s /usr/bin/python3 /usr/bin/python

# Install nodejs
RUN update-ca-certificates

WORKDIR /app

# install node 16
RUN touch install_node.sh
RUN curl -fsSL https://deb.nodesource.com/setup_18.x -o install_node.sh
RUN chmod +x install_node.sh && ./install_node.sh
RUN apt-get update
RUN apt-get install -y nodejs
RUN apt-get install -y uglifyjs
RUN npm install -g browserify
RUN npm install -g npm-run-all
RUN npm install -g closure-util

# Install nodejs
COPY python-cron python-cron
COPY startup.sh pre_startup.sh /
COPY ./timezone /etc/timezone
COPY sss sss
COPY packages packages
RUN chmod 755 /startup.sh && \
    chmod +s /startup.sh && \
    chmod 755 /pre_startup.sh && \
    chmod +s /pre_startup.sh && \
    groupadd -g 5000 oim && \
    useradd -g 5000 -u 5000 oim -s /bin/bash -d /app && \
    usermod -a -G sudo oim && \
    echo "oim  ALL=(ALL)  NOPASSWD: /startup.sh" > /etc/sudoers.d/oim && \
    chown -R oim.oim /app && \
    mkdir /container-config/ && \
    chown -R oim.oim /container-config/ && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    touch /app/rand_hash

# add health check
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin/health_check.sh -O /bin/health_check.sh
RUN chmod 755 /bin/health_check.sh

# add python cron
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin-python/scheduler/scheduler.py -O /bin/scheduler.py
RUN chmod 755 /bin/scheduler.py

# Add azcopy to container
RUN mkdir /tmp/azcopy/
RUN wget https://aka.ms/downloadazcopy-v10-linux -O /tmp/azcopy/azcopy.tar.gz
RUN cd /tmp/azcopy/ ; tar -xzvf azcopy.tar.gz
RUN cp /tmp/azcopy/azcopy_linux_amd64_10.25.1/azcopy /bin/azcopy

RUN chmod 755 /pre_startup.sh
# Install Python libs from requirements.txt.
FROM builder_base_govapp as python_libs_govapp

USER oim
RUN virtualenv /app/venv
RUN PATH=/app/.local/bin:$PATH
COPY --chown=oim:oim requirements.txt ./
COPY --chown=oim:oim src src
COPY --chown=oim:oim .git .git
COPY --chown=oim:oim package.json ./
# COPY --chown=oim:oim package-lock.json ./
COPY --chown=oim:oim profile.py ./
RUN ls -al /app/venv/bin
RUN /app/venv/bin/pip3 install -r requirements.txt
RUN /app/venv/bin/pip3 install npm
#\ && rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

RUN npm install --loglevel verbose
RUN npm run build

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_govapp
COPY --chown=oim:oim gunicorn.ini manage.py ./
RUN touch /app/.env

RUN /app/venv/python manage.py collectstatic --noinput

RUN mkdir /app/tmp/
RUN chmod 777 /app/tmp/

# IPYTHONDIR - Will allow shell_plus (in Docker) to remember history between sessions
# 1. will create dir, if it does not already exist
# 2. will create profile, if it does not already exist
#RUN mkdir /app/logs/.ipython
#RUN export IPYTHONDIR=/app/logs/.ipython/

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/pre_startup.sh"]

