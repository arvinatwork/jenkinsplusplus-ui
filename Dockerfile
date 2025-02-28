FROM python:3.7-alpine

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .
ENV FLASK_APP "app.py"

CMD [ "flask", "run", "--host=0.0.0.0" ]

# To build
#docker build -t jenkinsplusplus:v1.0.0 .
