FROM python:3.9-buster
ENV PYTHONPATH "${PYTHONPATH}:/app"
COPY . /app/
WORKDIR /app/
RUN pip install -U pip && pip3 install -r requirements.txt
ENV PYTHONUNBUFFERED=1
RUN pwd
RUN chmod u+x main.py
RUN python3 --version
CMD ["python3", "./main.py"]