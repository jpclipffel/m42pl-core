<!-- vim: set ft=Markdown ts=4 -->

# Installation

M42PL is divided into several packages and repositories. If you're starting on
the project, you may prefer to use a [container image](#container-images).

For more experienced users and developers, you may [install the project from source](#from-source).

## <a name="container-images"></a> Container images

Two container images are available:

* `jpclipffel/m42pl`: standard image, comes with everything pre-installed

```shell
docker pull jpclipffel/m42pl:latest
# Or
docker pull ghcr.io/jpclipffel/m42pl:latest
```

* `jpclipffel/m42pl-core`: base image, contains only `m42pl-core`

```shell
docker pull jpclipffel/m42pl-core:latest
# Or
docker pull ghcr.io/jpclipffel/m42pl-core:latest
```

## <a name="from-source"></a> From source

M42PL is built on several components (_core_, _commands_, _dispatchers_, _kvstores_ and _encoders_).

!!! info "Installation in a virtual environment"
    If is recomended to install M42PL into a dedicated virtual environement:
    `python -m venv m42pl && source m42pl/bin/activate`

!!! info "Installation in development mode"
    If you plan to make change to M42PL, install the component(s) with 
    `pip install -e <component>`

Install the core project `m42pl_core`:

```shell
git clone https://github.com/jpclipffel/m42pl-core
pip install m42pl-core
```

Install the core commands `m42pl_commands`:

```shell
git clone https://github.com/jpclipffel/m42pl-commands
pip install m42pl-commands
```

Install the core dispatchers `m42pl_dispatchers`:

```shell
git clone https://github.com/jpclipffel/m42pl-dispatchers
pip install m42pl-dispatchers
```

Install the core kvstores `m42pl_kvsotres`:

```shell
git clone https://github.com/jpclipffel/m42pl-kvstores
pip install m42pl-kvstores
```

Install the core encoders `m42pl_encoders`:

```shell
git clone https://github.com/jpclipffel/m42pl-encoders
pip install m42pl-encoders
```



---

[m42pl-image-dockerhub]: https://hub.docker.com/r/jpclipffel/m42pl
[m42pl-core-image-dockerhub]: https://hub.docker.com/r/jpclipffel/m42pl-core