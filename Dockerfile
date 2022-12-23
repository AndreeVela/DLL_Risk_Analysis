# preparing the instance

FROM python:3.9.16-slim-bullseye

RUN pip install --upgrade pip
RUN apt update && apt install -y make curl

WORKDIR ./dll_aams
COPY ./ /dll_aams

# application setup

RUN python3 -m venv .venv
RUN pip install -r requirements.txt
EXPOSE 8080

CMD gunicorn 'flaskr:create_app()'