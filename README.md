# Introduction

This code is for the talk of the Python Ireland meetup: https://www.meetup.com/pythonireland/events/270401360/


# Installation

This project uses `poetry` for the dependencies

```
pip3 install poetry
```

in the repository, just need to install the dependencies with

```
poetry install
```

and don't forget to execute the docker-compose

```
docker-compose up
```

After that, you can run the faust consumer with
```
poetry run faust -A consumer worker -l INFO --without-web
```

and run the producer via
```
poetry run uvicorn producer:app --port 8001
```

In this talk, I use Apache Kafka, Minio, Mailhog for the software components
FastAPI and Faust, aiokafka and aiosmtplib for the python components.

If you see any issue with the code or if you have remarks, please contribute and I will be happy to fix it.

Thank you,

Stéphane
