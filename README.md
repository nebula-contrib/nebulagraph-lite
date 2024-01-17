<div>
  <img src="https://github.com/wey-gu/nebulagraph-lite/assets/1651790/97b5dccb-bca1-4141-b426-03bcb3761a10" alt="NebulaGraph-Lite-logo" height="100" style="float:left;">
  <h1 style="margin-left:110px;">NebulaGraph Lite</h1>
</div>

Try NebulaGraph with `pip install`, on Linux/ WSL2 or even [Google Colab](https://bit.ly/nebula-colab), in container, rootless.

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://bit.ly/nebula-colab)
[![Jupyter](https://img.shields.io/badge/Jupyter-Supported-brightgreen)](https://github.com/jupyterlab/jupyterlab)
[![for NebulaGraph](https://img.shields.io/badge/Toolchain-NebulaGraph-blue)](https://github.com/vesoft-inc/nebula)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)


[![GitHub release (latest by date)](https://img.shields.io/github/v/release/wey-gu/nebulagraph-lite?label=release)](https://github.com/wey-gu/nebulagraph-lite/releases)
[![pypi-version](https://img.shields.io/pypi/v/nebulagraph-lite)](https://pypi.org/project/nebulagraph-lite/)
[![python-version](https://img.shields.io/badge/python-3.8%20|%203.9%20|%203.10%20|%203.11%20|%203.12-blue)](https://www.python.org/)

[![Build Checks](https://github.com/wey-gu/nebulagraph-lite/actions/workflows/release.yaml/badge.svg)](https://github.com/wey-gu/nebulagraph-lite/actions/workflows/release.yaml)

## How to use

> Install NebulaGraph Lite

```bash
pip3 install nebulagraph-lite
```

> Start NebulaGraph Lite

<table>
<tr>
<td> From Jupyter Notebook: </td> <td> From CLI: </td>
</tr>
<tr>
<td>

```python
from nebulagraph_lite import nebulagraph_let as ng_let

n = ng_let()

n.start()
```

</td>
<td>


```bash

nebulagraph start  

```


</td>
</tr>
</table>

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

## Supported Platforms

[![Ubuntu ✔](https://img.shields.io/badge/Ubuntu-✔-green?logo=ubuntu)](https://github.com/wey-gu/nebulagraph-lite)
[![Google Colab ✔](https://img.shields.io/badge/Google%20Colab-✔-green?logo=googlecolab)](https://github.com/wey-gu/nebulagraph-lite)
[![RockyLinux ✔](https://img.shields.io/badge/RockyLinux-✔-green?logo=rockylinux)](https://github.com/wey-gu/nebulagraph-lite)
[![Nested**Container** ✔](https://img.shields.io/badge/NestedContainer-✔-green?logo=docker)](https://github.com/wey-gu/nebulagraph-lite)
[![WSL2 ✔](https://img.shields.io/badge/WSL2-✔-green?logo=windows)](https://github.com/wey-gu/nebulagraph-lite)

## FAQ

<details>
  <summary>Click to see FAQ</summary>

### Why not docker?

With udocker, the opinionated subset docker running in user space, we could run docker images without root privilege, docker daemon.

Thus we support running inside docker container, WSL2, Google Colab.

### Can NebulaGraph-Lite run inside a container?

Yes! Say we are in a container that runs Ubuntu, we could run:

```bash
docker run -it --rm ubuntu:latest bash
# inside the container
apt update && apt install python3-pip curl -y
pip3 install nebulagraph-lite
python3
```

In python3:

```python
from nebulagraph_lite import nebulagraph_let as ng_let
n = ng_let(in_container=True)
n.start()
```

Or in shell:

```bash
nebulagraph --container start
```

### Does it support Windows?

Yes, it supports Windows with WSL2 or other Linux VMs with a Hypervisor.

### How to clean up?

- Step 1, from nebulagraph-lite, remove the udocker container and clean up the base path.

Python:

```python
n.stop()
n.clean_up()
```

Shell:

```bash
nebulagraph stop
nebulagraph cleanup
```

- Step 2, pip uninstall nebulagraph-lite and dependencies.

```bash
pip3 uninstall nebulagraph-lite udocker
```

- Step 3, remove the udocker files.

```bash
rm -rf ~/.udocker
```

</details>
