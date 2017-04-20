FROM smebberson/alpine-base:3.1.0
MAINTAINER Tom Ashley <tom@dataloop.io>

# Install dataloop basic requirements
RUN apk add --no-cache --update bash curl python python-dev py-pip gcc musl-dev linux-headers s6

# Install plugin_requirements dependencies
RUN apk add py-mysqldb py-psycopg2 libffi-dev openssl-dev

ADD agent/ /opt/dataloop/agent

# install pip requirements and make necessary dirs
RUN cd /opt/dataloop/agent/ && pip install -r /opt/dataloop/agent/requirements.txt && mkdir -p /etc/dataloop /var/log/dataloop /opt/dataloop

RUN sed -i '/MySQL-python/d' /opt/dataloop/agent/plugin_requirements.txt \
    && sed -i '/psycopg2/d' /opt/dataloop/agent/plugin_requirements.txt \
    && pip install -r /opt/dataloop/agent/plugin_requirements.txt
# add run scripts
ADD root/ /

# compile and cleanup/remove py files for pyc ?
RUN /usr/bin/python -m compileall /opt/dataloop/agent
RUN find /opt/dataloop/agent/dataloop_agent -path /opt/dataloop/agent/dataloop_agent/__init__.py -prune -o -name '*py' -print -exec rm -fv {} \;

# cleanup
RUN apk del python-dev gcc linux-headers binutils binutils-libs libstdc++ gmp isl

# expose the fingerprint
EXPOSE 8000