FROM m42pl-core:latest

COPY --chown=m42pl:m42pl m42pl-commands     ./m42pl-commands/
COPY --chown=m42pl:m42pl m42pl-dispatchers  ./m42pl-dispatchers/
COPY --chown=m42pl:m42pl m42pl-kvstores     ./m42pl-kvstores/
COPY --chown=m42pl:m42pl m42pl-encoders     ./m42pl-encoders/

RUN \
        pip install --user --no-warn-script-location -e  ./m42pl-commands    \
    &&  pip install --user --no-warn-script-location -e  ./m42pl-dispatchers \
    &&  pip install --user --no-warn-script-location -e  ./m42pl-kvstores    \
    &&  pip install --user --no-warn-script-location -e  ./m42pl-encoders

ENTRYPOINT ["python3", "-m", "m42pl"]
