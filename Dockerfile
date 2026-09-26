FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
CMD ["phantom-v8", "--audit", "--simulate-hid"]
