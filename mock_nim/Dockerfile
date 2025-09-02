FROM python:3.11-slim

WORKDIR /srv

RUN pip install --no-cache-dir fastapi==0.112.2 uvicorn==0.30.6

COPY server.py /srv/server.py

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]


