FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "realtime_api:app", "--host", "0.0.0.0", "--port", "8001"]