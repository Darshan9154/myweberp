# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn
RUN pip install gunicorn

# Make the uploads folder for storing uploaded files
RUN mkdir -p /app/uploads

# Expose port 80 for the application
EXPOSE 80

# Define environment variable to run Flask in production
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask application using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
