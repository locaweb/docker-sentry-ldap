FROM sentry:8.21.0
MAINTAINER Open Source Locaweb <opensource at locaweb.com.br> 

RUN apt-get -qq update && DEBIAN_FRONTEND=noninteractive apt-get install -y -q libxslt1-dev libxml2-dev libpq-dev libldap2-dev libsasl2-dev libssl-dev

COPY sentry.conf.py /etc/sentry/sentry.conf.py

COPY requirements.txt /tmp/

RUN pip install -r /tmp/requirements.txt

# cleanup
RUN apt-get remove -y -q libxslt1-dev libxml2-dev libpq-dev libldap2-dev libsasl2-dev libssl-dev
RUN rm -rf /var/lib/apt/lists/*
RUN rm /tmp/requirements.txt
