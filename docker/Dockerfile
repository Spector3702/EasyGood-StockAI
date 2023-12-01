FROM gcr.io/stockmarketindexai/linebot-lstm:latest

COPY models models
COPY server server

CMD ["python", "server/app.py", "--driver", "/usr/bin/chromedriver"]
