FROM m42pl-core:latest

# Work on /m42pl
WORKDIR /m42pl

# Install psutil
# USER root
# RUN apk add py3-psutil
# USER m42pl

# Copy M42PL sources
COPY --chown=m42pl:m42pl m42pl-commands m42pl-commands/
COPY --chown=m42pl:m42pl m42pl-dispatchers m42pl-dispatchers/
COPY --chown=m42pl:m42pl m42pl-kvstores m42pl-kvstores/
COPY --chown=m42pl:m42pl m42pl-encoders m42pl-encoders/

# Install build tools
# USER root
# RUN apt-get update && apt-get install -y build-essential make gcc
# USER m42pl

# Install M42PL
RUN \
       pip install --user --no-warn-script-location -e m42pl-commands \
    && pip install --user --no-warn-script-location -e m42pl-dispatchers \
    && pip install --user --no-warn-script-location -e m42pl-kvstores \
    && pip install --user --no-warn-script-location -e m42pl-encoders

# Entry point
ENTRYPOINT [ "python3", "-m", "m42pl" ]
