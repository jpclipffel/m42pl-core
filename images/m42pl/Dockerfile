FROM m42pl-core:latest as build

USER root

ENV PATH="/opt/m42pl/bin:$PATH"

RUN apt-get update
RUN apt-get install -y --no-install-recommends build-essential gcc

COPY m42pl-commands     ./m42pl-commands/
COPY m42pl-dispatchers  ./m42pl-dispatchers/
COPY m42pl-kvstores     ./m42pl-kvstores/
COPY m42pl-encoders     ./m42pl-encoders/

RUN \
        pip install ./m42pl-commands    \
    &&  pip install ./m42pl-dispatchers \
    &&  pip install ./m42pl-kvstores    \
    &&  pip install ./m42pl-encoders


FROM m42pl-core:latest as runtime

USER m42pl

COPY --from=build --chown=m42pl /opt/m42pl /opt/m42pl

ENV PATH="/opt/m42pl/bin:$PATH"
CMD ["python3", "-m", "m42pl"]
