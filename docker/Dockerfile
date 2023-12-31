FROM debian:stable-slim

# install packages
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  curl \
  python3-full \
#  python3-requests \
#  python3-bs4 \
#  python3-sqlite-fts4 \
  && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
RUN . /opt/venv/bin/activate && pip install requests bs4 sqlite-fts4 google-generativeai

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /opt/app

ENTRYPOINT [ ]
