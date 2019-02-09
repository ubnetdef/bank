FROM python:2.7
ENV PYTHONUNBUFFERED=1

RUN mkdir /opt/bank-api
WORKDIR /opt/bank-api

COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--pid", "app.pid", "--workers", "4", "run:app"]
