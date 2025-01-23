FROM python:3.13.0

RUN pip install poetry==1.8.4

WORKDIR /myapp

COPY . /myapp

RUN poetry install 

ENTRYPOINT ["python", "personal_assistance.py"]