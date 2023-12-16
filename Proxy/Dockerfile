# Use the official Python image as base image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Copy the Python script files into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Grant access to the serial port
RUN usermod -a -G dialout root

# Run the application
CMD ["python", "server.py"]
