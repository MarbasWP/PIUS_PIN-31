FROM python:3.7-slim

RUN apt-get update && apt-get install -y libpq-dev gcc

WORKDIR /app

COPY requirements.txt /app

RUN pip3 install -r requirements.txt --no-cache-dir || (echo 'Installation failed' && exit 1)

COPY ./ .

CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ] 
