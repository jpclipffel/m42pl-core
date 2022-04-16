FROM python:3.10

RUN adduser --home /opt/m42pl m42pl
USER m42pl
WORKDIR /opt/m42pl

COPY --chown=m42pl:m42pl m42pl      ./m42pl-core/m42pl
COPY --chown=m42pl:m42pl setup.py   ./m42pl-core/setup.py

RUN pip install --user --no-warn-script-location -e ./m42pl-core
