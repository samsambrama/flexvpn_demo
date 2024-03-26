FROM python:latest
WORKDIR /app
COPY ./ciscopi.py /app/ciscopi.py
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN python3 -m pip install pipenv && \
    pip install --upgrade pip && \
    apt-get update
RUN pipenv install
CMD ["python3", "ciscopi.py"]
