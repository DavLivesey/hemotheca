FROM python:3.11-alpine

RUN adduser -D botuser
USER botuser

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY --chown=botuser:botuser . .

CMD ["python", "app.py"]