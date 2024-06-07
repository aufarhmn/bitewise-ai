FROM python:3.12.3-bullseye

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=main.py

EXPOSE 5200

CMD ["waitress-serve", "--port=5200", "--call", "main:create_app"]