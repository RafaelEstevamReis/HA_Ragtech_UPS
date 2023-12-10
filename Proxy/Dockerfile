# Use the official Python image as base image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

RUN pip install flask

# Copy the Python script files into the container
COPY . /app

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "server.py"]
