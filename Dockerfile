FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port used by the application
EXPOSE 5023

# The run.py already configures host='0.0.0.0' and port=5023
CMD ["python", "app.py"]
