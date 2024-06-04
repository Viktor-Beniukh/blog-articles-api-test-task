FROM python:3.10 as requirements-stage

WORKDIR /tmp


RUN pip install poetry


COPY ./pyproject.toml ./poetry.lock* /tmp/


RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


FROM python:3.10.9-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


WORKDIR /code

COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && apt-get -y install libpq-dev gcc wget unzip curl gnupg --no-install-recommends

# Install Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] https://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean

# Copy chromedriver from project root
COPY chromedriver /usr/local/bin/
RUN chmod +x /usr/local/bin/chromedriver


RUN python -m pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


COPY . /code/


RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user

RUN chown -R django-user:django-user /code/
RUN chmod -R 755 /code/

USER django-user
