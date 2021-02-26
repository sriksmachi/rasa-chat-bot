FROM rasa/rasa:2.3.0-full 

USER root

WORKDIR /app
COPY . /app
COPY ./data /app/data

RUN  rasa train

VOLUME /app
VOLUME /app/data
VOLUME /app/models

# Don't use root user to run code
USER 1001

CMD [ "run","-m","/app/models","--enable-api","--cors","*" ]