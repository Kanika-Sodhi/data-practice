FROM datamechanics/spark:3.2.1-hadoop-3.3.1-java-11-scala-2.12-python-3.8-dm18

USER root

WORKDIR /app

RUN pip install --upgrade pip

RUN ln -s /usr/bin/python3 /usr/bin/python
COPY  requirements.txt .
RUN pip3 install -r requirements.txt

COPY ingest.py ./
COPY log_handler.py ./
COPY main.py ./
COPY parameter_file.py ./
COPY persist.py ./
COPY pipeline.py ./
COPY recipe_difficulty_insights.py ./
COPY transform.py ./


ENTRYPOINT ./main.py