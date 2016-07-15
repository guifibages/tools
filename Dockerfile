FROM python:3-onbuild

MAINTAINER Ignacio Torres Masdeu <i@itorres.net>

ENTRYPOINT ["/usr/src/app/gbtools"]

CMD ["usage"]
