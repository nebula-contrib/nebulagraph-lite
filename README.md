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

## Acknowledgements

- udocker, https://github.com/indigo-dc/udocker
- docker-in-colab, https://github.com/drengskapur/docker-in-colab
- NebulaGraph Docker, https://github.com/vesoft-inc/nebula-docker-compose
