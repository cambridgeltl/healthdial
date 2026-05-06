FROM python:3.10-slim-bullseye

ENV CONTAINER_HOME=/server
WORKDIR $CONTAINER_HOME
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ADD ./requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p final_submit

WORKDIR $CONTAINER_HOME
EXPOSE 5000
CMD ["python","app.py"]
