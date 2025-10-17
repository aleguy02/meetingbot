FROM python:3.13-slim

WORKDIR /meetingbot

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
