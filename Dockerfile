FROM python:3.10-slim

# Install Java 17 (required by Timefold)
RUN apt-get update && apt-get install -y openjdk-17-jdk

WORKDIR /app

COPY . .

# -e flag allows the python files to be editable, which allows for hot-reload functionality
RUN pip install -e .
