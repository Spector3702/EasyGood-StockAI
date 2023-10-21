FROM tensorflow/tensorflow:latest

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY models models
COPY server server

CMD ["python", "server/app.py"]
