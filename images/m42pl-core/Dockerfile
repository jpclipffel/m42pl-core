FROM python:3.10-slim as build

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

RUN python3 -m venv /opt/m42pl
ENV PATH="/opt/m42pl/bin:$PATH"

COPY m42pl      ./m42pl-core/m42pl
COPY setup.py   ./m42pl-core/setup.py

RUN pip install ./m42pl-core


FROM python:3.10-slim as runtime

RUN adduser m42pl
USER m42pl
COPY --from=build --chown=m42pl /opt/m42pl /opt/m42pl

ENV PATH="/opt/m42pl/bin:$PATH"
CMD ["python"]
