FROM tensorflow/tensorflow:2.14.0rc0

# Install system dependencies for wget, unzip, and other utilities
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    ca-certificates \
    xvfb \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    fonts-liberation \
    libappindicator1 \
    libnspr4 \
    libasound2 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    libappindicator3-1 \
    lsb-release \
    xdg-utils

# Download and install Chrome
RUN wget https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chrome-linux64.zip \
    && unzip chrome-linux64.zip -d /opt/ \
    && ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome \
    && rm chrome-linux64.zip

# Download and install ChromeDriver
RUN wget -O chromedriver-linux64.zip https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/119.0.6045.105/linux64/chromedriver-linux64.zip && \
    unzip chromedriver-linux64.zip -d /opt/ && \
    chmod +x /opt/chromedriver-linux64/chromedriver && \
    ln -s /opt/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    rm chromedriver-linux64.zip

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --ignore-installed -r requirements.txt

COPY models models
COPY server server

CMD ["python", "server/app.py", "--driver", "/usr/bin/chromedriver"]
