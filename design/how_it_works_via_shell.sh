# Install udocker

pip3 install udocker
udocker install

# Create Folders

mkdir -p ~/.nebulagraph/lite/data/meta0
mkdir -p ~/.nebulagraph/lite/logs/meta0
mkdir -p ~/.nebulagraph/lite/data/storage0
mkdir -p ~/.nebulagraph/lite/logs/storage0
mkdir -p ~/.nebulagraph/lite/logs/graph

# Change Directory
cd ~/.nebulagraph/lite

# Run NebulaGraph MetaD

# udocker --debug run --rm \
#   --user=root \
#   -v /home/w/.nebulagraph/lite/data/meta0:/data/meta \
#   -v /home/w/.nebulagraph/lite/logs/meta0:/logs \
#   vesoft/nebula-metad:v3 \
#   --meta_server_addrs=127.0.0.1:9559 \
#   --local_ip=127.0.0.1 \
#   --ws_ip=127.0.0.1 \
#   --port=9559 \
#   --ws_http_port=19559 \
#   --data_path=/data/meta \
#   --log_dir=/logs \
#   --v=0 \
#   --minloglevel=0

udocker --debug create \
  --name=nebula-metad \
  vesoft/nebula-metad:v3

udocker --allow-root setup --execmode=F1 nebula-metad

udocker --debug run \
  --user=root \
  -v /home/w/.nebulagraph/lite/data/meta0:/data/meta \
  -v /home/w/.nebulagraph/lite/logs/meta0:/logs \
  nebula-metad \
  --meta_server_addrs=127.0.0.1:9559 \
  --local_ip=127.0.0.1 \
  --ws_ip=127.0.0.1 \
  --port=9559 \
  --ws_http_port=19559 \
  --data_path=/data/meta \
  --log_dir=/logs \
  --v=0 \
  --minloglevel=0

# Run NebulaGraph GraphD
udocker --debug run --rm \
  --user=root \
  -v /home/w/.nebulagraph/lite/logs/graph:/logs \
  vesoft/nebula-graphd:v3 \
  --meta_server_addrs=127.0.0.1:9559 \
  --local_ip=127.0.0.1 \
  --ws_ip=127.0.0.1 \
  --port=39669 \
  --ws_http_port=19669 \
  --log_dir=/logs \
  --v=0 \
  --minloglevel=0

# Run NebulaGraph StorageD

# udocker --debug run --rm \
#   --user=root \
#   -v /home/w/.nebulagraph/lite/data/storage0:/data/storage \
#   -v /home/w/.nebulagraph/lite/logs/storage0:/logs \
#   vesoft/nebula-storaged:v3 \
#   --meta_server_addrs=127.0.0.1:9559 \
#   --local_ip=127.0.0.1 \
#   --ws_ip=127.0.0.1 \
#   --port=9779 \
#   --ws_http_port=19779 \
#   --data_path=/data/storage \
#   --log_dir=/logs \
#   --v=0 \
#   --minloglevel=0

udocker --debug create \
  --name=nebula-storaged \
  vesoft/nebula-storaged:v3

udocker --allow-root setup --execmode=F1 nebula-storaged

udocker --debug run \
  --user=root \
  -v /home/w/.nebulagraph/lite/data/storage0:/data/storage \
  -v /home/w/.nebulagraph/lite/logs/storage0:/logs \
  nebula-storaged \
  --meta_server_addrs=127.0.0.1:9559 \
  --local_ip=127.0.0.1 \
  --ws_ip=127.0.0.1 \
  --port=9779 \
  --ws_http_port=19779 \
  --data_path=/data/storage \
  --log_dir=/logs \
  --v=0 \
  --minloglevel=0

# Run NebulaGraph Console

# i.e. add hosts
udocker --debug run --rm \
  vesoft/nebula-console:v3 \
  -addr 127.0.0.1 -port 39669 -u root -p nebula -e 'ADD HOSTS "127.0.0.1":9779'
