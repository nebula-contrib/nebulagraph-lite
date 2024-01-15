import os
import subprocess
import time

from urllib.request import urlretrieve

from nebulagraph_lite.utils import (
    retry,
    fancy_print,
    fancy_dict_print,
    BANNER_ASCII,
    get_pid_by_port,
    kill_process_by_pid,
    process_listening_on_port,
)

LOCALHOST_V4 = "127.0.0.1"
DEFAULT_GRAPHD_PORT = 9669
BASE_PATH = os.path.expanduser("~/.nebulagraph/lite")
COLAB_BASE_PATH = "/content/.nebulagraph/lite"

# Data set
BASKETBALLPLAYER_DATASET_URL = "https://raw.githubusercontent.com/vesoft-inc/nebula-console/master/data/basketballplayer.ngql"


class NebulaGraphLet:
    def __init__(
        self,
        host: str = LOCALHOST_V4,
        port: int = DEFAULT_GRAPHD_PORT,
        base_path: str = BASE_PATH,
        debug=False,
        clean_up=False,
        in_container=False,
    ):
        self.host = host if host is not None else LOCALHOST_V4
        self.port = port if port is not None else DEFAULT_GRAPHD_PORT
        self.base_path = base_path if base_path is not None else BASE_PATH

        if clean_up:
            self.clean_up()

        assert (
            os.path.expanduser("~") in self.base_path
        ), "Base path must be under current user's home directory"

        self.on_ipython = False
        try:
            from IPython import get_ipython

            ipython = get_ipython()
            self.on_ipython = bool(ipython)
        except:
            pass

        if self.on_ipython:
            _path = get_ipython().getoutput("which udocker")
            assert (
                _path
            ), "udocker's path cannot be determined, please specify its base path manually"
            self._python_bin_path = os.path.dirname(_path[0])
        else:
            self._python_bin_path = os.path.dirname(os.sys.executable)
            result = subprocess.run(
                f"{self._python_bin_path}/udocker --allow-root --help",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode != 0:
                _path = subprocess.getoutput("which udocker")
                if _path:
                    self._python_bin_path = os.path.dirname(_path)
                else:
                    raise Exception(
                        "udocker not found. Please install or link it manually to your PATH."
                    )

        self._debug = debug if debug is not None else False

        self.on_colab = self._is_running_on_colab()
        if self.on_colab:
            self.base_path = COLAB_BASE_PATH

        self.in_container = in_container if in_container is not None else False

        self.create_nebulagraph_lite_folders()

    def _is_running_on_colab(self):
        try:
            from IPython import get_ipython

            if "google.colab" in str(get_ipython()):
                fancy_print("Info: Detected that we are running on Google Colab!")
                # Thanks to https://github.com/drengskapur/docker-in-colab by drengskapur
                get_ipython().system("pip install udocker > /dev/null")
                get_ipython().system("udocker --allow-root install > /dev/null")
                get_ipython().system("useradd -m user > /dev/null")
                return True
        except Exception as e:
            if self._debug:
                fancy_dict_print({"error": e})
            return False

    def clean_up(self):
        if self.base_path == "/":
            raise Exception(
                "Opps, you are trying to delete the whole root directory!"
            )
        try:
            os.system(f"rm -rf {self.base_path}")
        except Exception as e:
            fancy_dict_print(
                {
                    "error": str(e),
                    "base_path": self.base_path,
                }
            )
            raise Exception(
                "nebulagraph_lite folders deletion failed, "
                "please check if you have the permission to delete folders in "
                f"{self.base_path}"
            )

    def create_nebulagraph_lite_folders(self):
        try:
            os.makedirs(os.path.join(self.base_path, "data_set"), exist_ok=True)
            os.makedirs(os.path.join(self.base_path, "data/meta0"), exist_ok=True)
            os.makedirs(os.path.join(self.base_path, "logs/meta0"), exist_ok=True)
            os.makedirs(
                os.path.join(self.base_path, "data/storage0"), exist_ok=True
            )
            os.makedirs(
                os.path.join(self.base_path, "logs/storage0"), exist_ok=True
            )
            os.makedirs(os.path.join(self.base_path, "logs/graph"), exist_ok=True)

            if self.on_colab:
                from IPython import get_ipython

                get_ipython().system(f"chown -R user:user {self.base_path}")

        except Exception as e:
            fancy_dict_print(
                {
                    "error": str(e),
                    "base_path": self.base_path,
                }
            )
            raise Exception(
                "nebulagraph_lite folders creation failed, "
                "please check if you have the permission to create folders in "
                f"{self.base_path}"
            )

    def _run_udocker_on_colab(self, command: str):
        from IPython import get_ipython

        result = get_ipython().system(f'su - user -c "udocker {command}"')
        return result

    @retry((Exception,), tries=3, delay=5, backoff=3)
    def _run_udocker(self, command: str):
        if self.on_colab:
            return self._run_udocker_on_colab(command)
        udocker_command_prefix = os.path.join(self._python_bin_path, "udocker")
        if self.in_container:
            udocker_command_prefix = udocker_command_prefix + " --allow-root"
        udocker_command = f"{udocker_command_prefix} {command}"
        result = subprocess.run(
            udocker_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = result.stdout, result.stderr
        if result.returncode != 0:
            fancy_dict_print(
                {
                    "udocker command": f"udocker {udocker_command}",
                    "error": error.decode(),
                },
            )
            raise Exception(
                f"udocker command failed with return code {result.returncode}"
            )
        if output and self._debug:
            fancy_print(f"Info: [DEBUG] udocker command output:\n{output.decode()}")
        return result

    def _run_udocker_ps_filter(self, filter: str):
        self._run_udocker(f"ps | grep {filter}")

    def _run_udocker_background_on_colab(self, command: str):
        from IPython import get_ipython

        if not self._debug:
            redirect_clause = "> /dev/null 2>&1"
        else:
            redirect_clause = ""
        get_ipython().system(
            f'nohup su - user -c "udocker {command}" {redirect_clause} &'
        )

    def _run_udocker_background(self, command: str):
        if self.on_colab:
            self._run_udocker_background_on_colab(command)
            return

        udocker_command_prefix = os.path.join(self._python_bin_path, "udocker")
        if self.in_container:
            udocker_command_prefix = udocker_command_prefix + " --allow-root"
        udocker_command = f"{udocker_command_prefix} {command} &"
        subprocess.Popen(
            udocker_command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def udocker_init(self):
        self._run_udocker("install")

    def udocker_pull(self, image: str):
        self._run_udocker(f"pull {image}")

    def udocker_pull_backgroud(self, image: str):
        self._run_udocker_background(f"pull {image}")

    def _try_shoot_service(self, service: str):
        try:
            self._run_udocker(
                f"ps | grep {service} | awk '{{print $1}}' | xargs -I {{}} udocker --allow-root rm -f {{}}"
            )
            # TODO: use psutil to kill the process
            os.system(f"killall nebula-{service} > /dev/null 2>&1")
        except Exception as e:
            if self._debug:
                fancy_print(f"Info: [DEBUG] failed to shoot {service}: {str(e)}")

    def _try_shoot_all_services(self):
        self._try_shoot_service("graphd")
        time.sleep(5)
        self._try_shoot_service("storaged")
        time.sleep(5)
        self._try_shoot_service("metad")

    def start_metad(self, shoot=False):
        if shoot:
            self._try_shoot_service("metad")

        udocker_create_command = "ps | grep metad || udocker --debug --allow-root create --name=nebula-metad vesoft/nebula-metad:v3"
        if self._debug:
            fancy_print(
                "Info: [DEBUG] creating metad container... with command:"
                f"\nudocker {udocker_create_command}"
            )
        self._run_udocker(udocker_create_command)

        # fakechroot is used, see #18
        # TODO: leverage F2 in MUSL/Alpine Linux
        udocker_setup_command = "--debug setup --execmode=F1 nebula-metad"
        self._run_udocker(udocker_setup_command)

        udocker_command = (
            f"run --rm --user=root -v "
            f"{self.base_path}/data/meta0:/data/meta -v "
            f"{self.base_path}/logs/meta0:/logs nebula-metad "
            f"--meta_server_addrs={self.host}:9559 --local_ip={self.host} "
            f"--ws_ip={self.host} --port=9559 --ws_http_port=19559 "
            f"--data_path=/data/meta --log_dir=/logs --v=0 --minloglevel=0"
        )
        if self._debug:
            fancy_print(
                "Info: [DEBUG] starting metad... with command:"
                f"\nudocker {udocker_command}"
            )
        self._run_udocker_background(udocker_command)
        time.sleep(10)
        if not self.on_colab:
            process_listening_on_port(9559)

    def start_graphd(self):
        self._try_shoot_service("graphd")

        udocker_create_command = "ps | grep graphd || udocker --debug --allow-root create --name=nebula-graphd vesoft/nebula-graphd:v3"
        if self._debug:
            fancy_print(
                "Info: [DEBUG] creating graphd container... with command:"
                f"\nudocker {udocker_create_command}"
            )
        self._run_udocker(udocker_create_command)

        udocker_command = (
            f"run --rm --user=root -v "
            f"{self.base_path}/logs/graph:/logs nebula-graphd "
            f"--meta_server_addrs={self.host}:9559 --local_ip={self.host} "
            f"--ws_ip={self.host} --port={self.port} --ws_http_port=19669 "
            f"--log_dir=/logs --v=0 --minloglevel=0"
        )
        if self._debug:
            fancy_print(
                "Info: [DEBUG] starting graphd... with command:"
                f"\nudocker {udocker_command}"
            )
        self._run_udocker_background(udocker_command)
        time.sleep(10)
        if not self.on_colab:
            # self._run_udocker_ps_filter("graphd")
            process_listening_on_port(self.port)

    def activate_storaged(self):
        udocker_command = (
            f"run --rm "
            f"vesoft/nebula-console:v3 "
            f"-addr {self.host} -port {self.port} -u root -p nebula -e 'ADD HOSTS \"{self.host}\":9779'"
        )
        self._run_udocker_background(udocker_command)
        time.sleep(10)
        udocker_command = (
            f"run --rm "
            f"vesoft/nebula-console:v3  "
            f"-addr {self.host} -port {self.port} -u root -p nebula -e 'SHOW HOSTS'"
        )
        self._run_udocker_background(udocker_command)

    def load_basketballplayer_dataset(self):
        url = BASKETBALLPLAYER_DATASET_URL
        try:
            urlretrieve(url, f"{self.base_path}/data_set/basketballplayer.ngql")
        except Exception as e:
            fancy_dict_print(
                {
                    "message": "Failed to download basketballplayer dataset, please check your network connection",
                    "error": str(e),
                    "url": url,
                }
            )
            raise Exception(
                f"Failed to download basketballplayer dataset from {url}"
            )

        udocker_command = (
            f"run --rm -v {self.base_path}/data_set:/root/data "
            f"vesoft/nebula-console:v3 "
            f"-addr {self.host} -port {self.port} -u root -p nebula -e ':play basketballplayer'"
        )
        try:
            time.sleep(10)
            self._run_udocker(udocker_command)
        except Exception as e:
            fancy_dict_print(
                {
                    "message": "Failed to load basketballplayer dataset, probably because the graphd is not ready yet or the cluster is not healthy, try cleaning up the base path and start again",
                    "error": str(e),
                    "udocker_command": udocker_command,
                }
            )
            fancy_dict_print(
                {
                    "Info:": "Failed to load basketballplayer dataset, probably because the graphd is not ready yet or the cluster is not healthy, try this later from the console manually",
                    "command": f"udocker {udocker_command}",
                    "error": str(e),
                }
            )

    def start_storaged(self, shoot=False):
        if shoot:
            self._try_shoot_service("storaged")

        udocker_create_command = "ps | grep storaged || udocker --debug --allow-root create --name=nebula-storaged vesoft/nebula-storaged:v3"
        if self._debug:
            fancy_print(
                "Info: [DEBUG] creating storaged container... with command:"
                f"\nudocker {udocker_create_command}"
            )
        self._run_udocker(udocker_create_command)

        # fakechroot is used, see #18
        # TODO: leverage F2 in MUSL/Alpine Linux
        udocker_setup_command = "--debug setup --execmode=F1 nebula-storaged"
        self._run_udocker(udocker_setup_command)

        udocker_command = (
            f"run --rm --user=root -v "
            f"{self.base_path}/data/storage0:/data/storage -v "
            f"{self.base_path}/logs/storage0:/logs nebula-storaged "
            f"--meta_server_addrs={self.host}:9559 --local_ip={self.host} "
            f"--ws_ip={self.host} --port=9779 --ws_http_port=19779 "
            f"--data_path=/data/storage --log_dir=/logs --v=0 --minloglevel=0"
        )
        if self._debug:
            fancy_print(
                "Info: [DEBUG] starting storaged... with command:"
                f"\nudocker {udocker_command}"
            )

        self._run_udocker_background(udocker_command)
        time.sleep(20)
        if not self.on_colab:
            # self._run_udocker_ps_filter("storaged")
            pass

    def start(self, fresh=False):
        shoot = bool(fresh)
        self.udocker_init()
        # async pull images
        self.udocker_pull("vesoft/nebula-metad:v3")
        self.udocker_pull_backgroud("vesoft/nebula-graphd:v3")
        self.start_metad(shoot=shoot)
        self.udocker_pull_backgroud("vesoft/nebula-storaged:v3")
        self.start_graphd()
        self.start_storaged(shoot=shoot)
        time.sleep(10)
        self.activate_storaged()
        self.udocker_pull("vesoft/nebula-console:v3")
        time.sleep(20)
        fancy_print("Info: loading basketballplayer dataset...")
        self.load_basketballplayer_dataset()
        fancy_print(BANNER_ASCII)
        fancy_print("[ OK ] nebulagraph_lite started successfully!", "purple")
        self.docker_ps()

    def check_status(self):
        self._run_udocker_ps_filter("metad")
        self._run_udocker_ps_filter("graphd")
        self._run_udocker_ps_filter("storaged")

    def docker_ps(self):
        self._run_udocker("ps")

    def stop(self):
        """
        Stop NebulaGraph-Lite services gracefully.
        """
        # We should stop graphd first, then storaged and finally metad
        # We leverage killall to stop all services and sleep 10 seconds per service
        # stop graphd
        self._try_shoot_service("graphd")
        # stop storaged
        storaged_pid = get_pid_by_port(9779)
        try:
            kill_process_by_pid(storaged_pid)
        except Exception as e:
            if self._debug:
                fancy_print(f"Info: [DEBUG] error when kill storaged, {e}")
        time.sleep(15)
        # stop metad by send signal to the process
        metad_pid = get_pid_by_port(9559)
        try:
            kill_process_by_pid(metad_pid)
        except Exception as e:
            if self._debug:
                fancy_print(f"Info: [DEBUG] error when kill metad, {e}")

    def shutdown(self):
        """
        Shutdown the NebulaGraph-Lite services in quick way.
        """
        if self.on_colab:
            self._run_udocker(
                "ps | grep nebula | awk '{print $1}' | xargs -I {} udocker --allow-root rm -f {}"
            )
            self._try_shoot_all_services()
            return

        # in other environments, we cannot assume awk/xargs are installed
        # let's get the container ids first
        try:
            result = self._run_udocker("ps | grep nebula").stdout.decode()
            container_ids = [line.split()[0] for line in result.split("\n") if line]
            if container_ids:
                self._run_udocker(f"rm {' '.join(container_ids)}")
        except Exception as e:
            if self._debug:
                fancy_print(f"Info: [DEBUG] error when udocker ps, {e}")

        self._try_shoot_all_services()

    def print_docker_ps(self):
        result = self.docker_ps()
        fancy_dict_print({"docker ps": result})
