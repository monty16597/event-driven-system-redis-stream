FROM python:3.9-alpine

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Install necessary dependencies
RUN pip3 install redis && \
    pip3 install flask

# Copy your Python application code into the container
COPY . /app

CMD ["python3", "main.py"]


