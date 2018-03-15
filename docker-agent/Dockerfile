# Use an official Python runtime as a parent image
FROM python:3.6.4

# Set the working directory to /app
WORKDIR /app

# Add the requirements.txt to the WORKDIR's top level.
ADD ./games/a/docker/requirements.txt /app/requirements.txt

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the current directory contents into the container at /app
ADD . /app

# Make port 80 available to the world outside this container
EXPOSE 10080

# Define environment variable
ENV NAME Agent

# Run app.py when the container launches
WORKDIR /app/games
CMD ["python", "-m", "a.docker.run"]
