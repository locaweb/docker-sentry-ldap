FROM sentry:9.1-onbuild
MAINTAINER Open Source Locaweb <opensource at locaweb.com.br>

RUN apt-get -qq update && DEBIAN_FRONTEND=noninteractive apt-get install -y -q libxslt1-dev libxml2-dev libpq-dev libldap2-dev libsasl2-dev libssl-dev sysvinit-utils procps

COPY sentry.conf.py /etc/sentry/sentry.conf.py

COPY req.txt /tmp/

RUN pip install -r /tmp/req.txt

# cleanup
RUN apt-get remove -y -q libxslt1-dev libxml2-dev libpq-dev libldap2-dev libsasl2-dev libssl-dev
RUN rm -rf /var/lib/apt/lists/*
RUN rm /tmp/req.txt
