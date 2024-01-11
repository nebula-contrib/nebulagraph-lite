# NebulaGraph Lite

[![for NebulaGraph](https://img.shields.io/badge/Toolchain-NebulaGraph-blue)](https://github.com/vesoft-inc/nebula)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![Jupyter](https://img.shields.io/badge/Jupyter-Supported-brightgreen)](https://github.com/jupyterlab/jupyterlab)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/wey-gu/nebulagraph-lite?label=Version)](https://github.com/wey-gu/nebulagraph-lite/releases)
[![pypi-version](https://img.shields.io/pypi/v/nebulagraph-lite)](https://pypi.org/project/nebulagraph-lite/)
[![python-version](https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11%20|%203.12-blue)](https://www.python.org/)

Try NebulaGraph with `pip install`, on Linux/ WSL2 or even [Google Colab](https://bit.ly/nebula-colab)!

## How to use

> Install NebulaGraph Lite

```bash
pip3 install nebulagraph-lite
```

> Start NebulaGraph Lite from Jupyter Notebook

```python
from nebulagraph_lite import nebulagraph_let as ng_let

n = ng_let()

n.start()
```

Voilà! It'ts up and running already now!

## What's next

Play with `nebula3-python` or [ipython-ngql](https://github.com/wey-gu/ipython-ngql) and walk through the [Documentation](https://docs.nebula-graph.io/)!

```bash
pip3 install ipython-ngql
%load_ext ngql
```

And we could access it like:

```python
%ngql --address 127.0.0.1 --port 9669 --user root --password nebula
```

And query like:

```python
%ngql SHOW HOSTS;
```

## Other non-lite or less-lite options

Intrested in other play or production options?

### Production

- [Binary Packages](https://www.nebula-graph.io/download), if running on bare OS.
- [K8s Operator](https://github.com/vesoft-inc/nebula-operator), on K8s.
- [NebulaGrpah Cloud](https://www.nebula-graph.io/cloud), the managed NebulaGraph service.

### Play and Dev

- [Docker Compose](https://github.com/vesoft-inc/nebula-docker-compose), if you are comfortable on single server
- [nebula-up](https://github.com/wey-gu/nebula-up), one-liner test env installer on single server, support studio, dashboard, nebulagraph algorithm, exchange etc, all-in-one.
- [Docker Extension](https://github.com/nebula-contrib/nebulagraph-docker-ext), one-click on Docker Desktop(macOS, windows) on desktop machines, in GUI flavor.
- [Nebula-Operator-KinD](https://github.com/wey-gu/nebula-operator-kind), Nebula K8s Operator with K8s-in-Docker, one-liner test env with docker+k8s+nebulagrpah-operator, try NebulaGraph on K8s with ease on your single server.

## Acknowledgements

- udocker, https://github.com/indigo-dc/udocker
- docker-in-colab, https://github.com/drengskapur/docker-in-colab
- NebulaGraph Docker, https://github.com/vesoft-inc/nebula-docker-compose
