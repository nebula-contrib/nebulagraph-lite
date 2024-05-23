
# Host artifacts on Modelscope

## Build artifacts

```bash
git clone https://sdfsdfoph1ofdsaofdf@www.modelscope.cn/sdfsdfoph1ofdsaofdf/nebulagraph-lite.git
cd nebulagraph-lite/releases/3.8.0
docker save -o nebulagraph_lite_meta.tar vesoft/nebula-metad:v3
docker save -o nebulagraph_lite_storage.tar vesoft/nebula-storaged:v3
docker save -o nebulagraph_lite_graph.tar vesoft/nebula-graphd:v3
docker save -o nebulagraph_lite_console.tar vesoft/nebula-console:v3

tar -czvf nebulagraph_lite.tar.gz nebulagraph_lite_console.tar nebulagraph_lite_graph.tar nebulagraph_lite_meta.tar nebulagraph_lite_storage.tar

rm *.tar

# udocker engine

wget https://raw.githubusercontent.com/jorge-lip/udocker-builds/master/tarballs/udocker-englib-1.2.10.tar.gz
mv udocker-englib-1.2.10.tar.gz 1.2.10.tar.gz

# ngql dataset

wget https://raw.githubusercontent.com/vesoft-inc/nebula-console/master/data/basketballplayer.ngql
```

## Publish to Modelscope

```bash
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
sudo apt-get install git-lfs -y

git lfs install
git lfs track "*.tar.gz"

git add releases/3.8.0/*.tar.gz
git add releases/3.6.0/*.ngql

git commit -m "add artifacts"
git push origin master
```
