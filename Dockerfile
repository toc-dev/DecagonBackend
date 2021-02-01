FROM python:3.7

WORKDIR /decagon

ADD . /decagon
RUN pip install -r requirements.txt

#ENTRYPOINT ["bash","entrypoint.prod.sh"]

ENTRYPOINT ["python"]

#CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["app.py"]



#FROM python:alpine AS base
#
#WORKDIR /Decagon
#
#
#RUN apk update
#RUN apk add postgresql-dev gcc python3-dev musl-dev
#
##COPY requirements.txt .
#
##RUN pip install -r requirements.txt
#
##COPY . /Decagon
#
##EXPOSE 6001
#
#ADD . /Decagon
#RUN pip install -r requirements.txt
#
#ENTRYPOINT ["bash","entrypoint.prod.sh"]
#
#CMD ["python", "app.py"]