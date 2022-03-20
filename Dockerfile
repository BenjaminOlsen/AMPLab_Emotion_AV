#!/usr/bin/env bash

FROM python:3.7

# Export env settings
ENV TERM=xterm
ENV LANG C.UTF-8

# Add Tini. Tini operates as a process subreaper for jupyter. This prevents
# kernel crashes.
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /usr/bin/tini
RUN chmod +x /usr/bin/tini

RUN apt-get update && apt-get -y upgrade && apt-get install -y gosu && rm -rf /var/lib/apt/lists/*

RUN pip install -U --no-cache-dir essentia-tensorflow
RUN pip install --no-cache-dir jupyter matplotlib pandas scipy

EXPOSE 8888

RUN adduser -q --gecos "" --disabled-password mir

USER mir
COPY --chown=mir:mir jupyter_notebook_config.json /home/mir/.jupyter/
# COPY jupyter_notebook_config.json /root/.jupyter/

USER root

ADD start.sh /usr/local/bin

RUN mkdir /notebooks && chown -R mir:mir /notebooks
WORKDIR /notebooks

CMD ["start.sh", "tini", "-s", "--", "jupyter-notebook", "--allow-root", "--no-browser",  "--port",  "8888",  "--ip", "0.0.0.0"]
