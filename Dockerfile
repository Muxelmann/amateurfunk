FROM python:3.10.2-alpine

COPY ./src /code/src

WORKDIR /code

RUN pip install --no-cache-dir --upgrade -r src/requirements.txt

VOLUME [ "/code/instance" ]

EXPOSE 80

# nobody:users on unraid
USER 99:100

CMD ["gunicorn", "--conf", "src/gunicorn_conf.py", "--bind", "0.0.0.0:80", "src.wsgi:app"]
