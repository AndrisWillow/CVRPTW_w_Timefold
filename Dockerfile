FROM python:3.10-slim

# Install Java 17 (required by Timefold)
RUN apt-get update && apt-get install -y openjdk-17-jdk

WORKDIR /app

# Alternatively maybe since we have a volume we could run the pip install command in run time.
# This would make for a quite complex entrypoint however, haven't tested it.
COPY . .

RUN pip install .

EXPOSE 8080
CMD ["run-app"]
