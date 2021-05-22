FROM python:3

RUN apt-get install -y git

WORKDIR /server/

EXPOSE 80

CMD ["python", "/server/server.py"]