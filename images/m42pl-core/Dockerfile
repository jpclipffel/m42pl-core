FROM python:3.10-slim as build

# Install M42PL package dependencies
RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc

# Setup M42PL's venv
RUN python3 -m venv /opt/m42pl
ENV PATH="/opt/m42pl/bin:$PATH"

# Copy M42PL package
COPY m42pl      ./m42pl-core/m42pl
COPY setup.py   ./m42pl-core/setup.py

# Install M42PL
RUN pip install ./m42pl-core


# ---


FROM python:3.10-slim as runtime

# Add M42PL user
RUN adduser m42pl
USER m42pl

# Copy M42PL package
COPY --from=build --chown=m42pl /opt/m42pl /opt/m42pl

# Prepend M42PL's venv to path
ENV PATH="/opt/m42pl/bin:$PATH"
CMD ["python"]
