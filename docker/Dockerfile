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
RUN . /opt/venv/bin/activate && \
    pip install \
      requests bs4 sqlite-fts4 google-generativeai selenium

ENV PATH="/opt/venv/bin:$PATH"

# for chrome and selenium
# Set environment variables for Chrome
ENV DEBIAN_FRONTEND noninteractive

# Install dependencies for Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    python3 \
    python3-pip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Add Chrome's repository to sources
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'

# Install Google Chrome
RUN apt-get update && apt-get install -y google-chrome-stable xvfb \
    libxi6 \
    libgconf-2-4

# Install ChromeDriver
RUN CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE` \
    && wget -N http://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P ~/ \
    && unzip ~/chromedriver_linux64.zip -d ~/ \
    && mv -f ~/chromedriver /usr/local/bin/chromedriver \
    && chown root:root /usr/local/bin/chromedriver \
    && chmod 0755 /usr/local/bin/chromedriver \
    && rm ~/chromedriver_linux64.zip

# Install Selenium
RUN pip3 install selenium webdriver_manager

WORKDIR /opt/app

ENTRYPOINT [ ]
