FROM jpclipffel/m42pl-core:latest as build

# Switch to root for packages installation
USER root
ENV PATH="/opt/m42pl/bin:$PATH"

# Install M42PL packages dependencies
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc

# Copy M42PL packages
COPY m42pl-commands     ./m42pl-commands/
COPY m42pl-dispatchers  ./m42pl-dispatchers/
COPY m42pl-kvstores     ./m42pl-kvstores/
COPY m42pl-encoders     ./m42pl-encoders/

# Install M42PL packages
RUN \
        pip install ./m42pl-commands    \
    &&  pip install ./m42pl-dispatchers \
    &&  pip install ./m42pl-kvstores    \
    &&  pip install ./m42pl-encoders


# ---


FROM jpclipffel/m42pl-core:latest as runtime

# Swicth back to M42PL user
USER m42pl

# Copy M42PL packages
COPY --from=build --chown=m42pl /opt/m42pl /opt/m42pl

# Setup path and CMD to M42PL
ENV PATH="/opt/m42pl/bin:$PATH"
CMD ["python3", "-m", "m42pl"]
ENTRYPOINT ["python3", "-m", "m42pl"]
