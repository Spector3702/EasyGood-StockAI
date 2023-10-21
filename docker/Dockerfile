FROM tensorflow/tensorflow:2.14.0rc0

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r --ignore-installed requirements.txt

COPY models models
COPY server server

CMD ["python", "server/app.py"]
