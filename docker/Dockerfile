FROM debian:stable-slim

# install packages
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  curl \
  gpg \
  python3-full \
  libatomic1 \
  chromium \
  fonts-wqy-zenhei \
#  python3-requests \
#  python3-bs4 \
#  python3-sqlite-fts4 \
  && rm -rf /var/lib/apt/lists/*

# for Nodejs
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
RUN . /root/.bashrc && nvm install node

# python venv and packages
RUN python3 -m venv /opt/venv
RUN . /opt/venv/bin/activate && \
    pip install \
      requests bs4 google-generativeai psycopg2-binary pytz

# gmail sender
COPY ../module-gmail-sender/requirements.txt .
RUN . /opt/venv/bin/activate && \
    pip install -r requirements.txt
RUN rm requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /opt/app

ENTRYPOINT [ ]
