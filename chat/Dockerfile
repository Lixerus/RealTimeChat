FROM python:3.13.0-slim
WORKDIR /auth_service
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY ./src .
EXPOSE 8000
ENTRYPOINT ["fastapi", "run", "main.py", "--port", "8000"]