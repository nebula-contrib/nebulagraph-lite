import os
import subprocess
import time
import functools
from typing import List, Type

LOCALHOST_V4 = "127.0.0.1"
DEFAULT_GRAPHD_PORT = 9669
BASE_PATH = os.path.expanduser("~/.nebulagraph/lite")
COLAB_BASE_PATH = "/content/.nebulagraph/lite"


def retry(
    exceptions: List[Type[Exception]],
    tries: int = 4,
    delay: int = 1,
    backoff: int = 2,
) -> None:
    """
    A decorator for retrying a function with an exponential backoff.

    Parameters:
    exceptions: A tuple of exception types to catch and retry.
    tries: Maximum number of attempts. Default is 4.
    delay: Initial delay between retries in seconds. Default is 1 second.
    backoff: Backoff multiplier. Default is 2.
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal tries, delay
            while tries > 1:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Retrying in {delay} seconds...", e)
                    time.sleep(delay)
                    tries -= 1
                    delay *= backoff
            return func(*args, **kwargs)  # Last attempt without catching exceptions

        return wrapper

    return decorator


class nebulagraph_let:
    def __init__(
        self,
        host: str = LOCALHOST_V4,
        port: int = DEFAULT_GRAPHD_PORT,
        base_path: str = BASE_PATH,
        debug=False,
        clean_up=False,
    ):
        if clean_up:
            self.clean_up_base_path()

        self.host = host
        self.port = port
        self.base_path = base_path

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

        self._debug = debug

        self.on_colab = self._is_running_on_colab()
        if self.on_colab:
            self.base_path = COLAB_BASE_PATH

        self.create_nebulagraph_lite_folders()

    def _is_running_on_colab(self):
        try:
            from IPython import get_ipython

            if "google.colab" in str(get_ipython()):
                print("Detected that we are running on Google Colab!")
                # Thanks to https://github.com/drengskapur/docker-in-colab by drengskapur
                get_ipython().system("pip install udocker > /dev/null")
                get_ipython().system("udocker --allow-root install > /dev/null")
                get_ipython().system("useradd -m user > /dev/null")
                return True
        except:
            return False

    def clean_up_base_path(self):
        if self.base_path == "/":
            raise Exception(
                "Opps, you are trying to delete the whole root directory!"
            )
        try:
            os.system(f"rm -rf {self.base_path}")
        except Exception as e:
            print(e)
            raise Exception(
                "nebulagraph_lite folders deletion failed, "
                "please check if you have the permission to delete folders in "
                f"{self.base_path}"
            )

    def create_nebulagraph_lite_folders(self):
        try:
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
            print(e)
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
        udocker_command = f"{udocker_command_prefix} {command}"
        result = subprocess.run(
            udocker_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, error = result.stdout, result.stderr
        if result.returncode != 0:
            print(
                f"\033[1;31;40m\n{'*' * 50}\n{error.decode()}\n{'*' * 50}\n\033[0m"
            )
            raise Exception(
                f"udocker command failed with return code {result.returncode}"
            )
        if output and self._debug:
            print(
                f"\033[1;32;40m\n{'*' * 50}\n{output.decode()}\n{'*' * 50}\n\033[0m"
            )
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
        udocker_command = f"{udocker_command_prefix} {command} &"
        subprocess.Popen(
            udocker_command,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def udocker_init(self):
        self._run_udocker("install")

    def start_metad(self):
        udocker_command = (
            f"run --rm --user=root -v "
            f"{self.base_path}/data/meta0:/data/meta -v "
            f"{self.base_path}/logs/meta0:/logs vesoft/nebula-metad:v3 "
            f"--meta_server_addrs={self.host}:9559 --local_ip={self.host} "
            f"--ws_ip={self.host} --port=9559 --ws_http_port=19559 "
            f"--data_path=/data/meta --log_dir=/logs --v=0 --minloglevel=0"
        )
        if self._debug:
            print("starting metad... with command:" f"\n{udocker_command}")
        self._run_udocker_background(udocker_command)
        time.sleep(10)
        if not self.on_colab:
            self._run_udocker_ps_filter("metad")

    def start_graphd(self):
        udocker_command = (
            f"run --rm --user=root -v "
            f"{self.base_path}/logs/graph:/logs vesoft/nebula-graphd:v3 "
            f"--meta_server_addrs={self.host}:9559 --local_ip={self.host} "
            f"--ws_ip={self.host} --port={self.port} --ws_http_port=19669 "
            f"--log_dir=/logs --v=0 --minloglevel=0"
        )
        if self._debug:
            print("starting graphd... with command:" f"\n{udocker_command}")
        self._run_udocker_background(udocker_command)
        time.sleep(10)
        if not self.on_colab:
            self._run_udocker_ps_filter("graphd")

    def activate_storaged(self):
        udocker_command = (
            f"run --rm "
            f"vesoft/nebula-console:v3 "
            f"-addr {self.host} -port {self.port} -u root -p nebula -e 'ADD HOSTS \"{self.host}\":9779'"
        )
        self._run_udocker_background(udocker_command)
        time.sleep(10)
        # TODO: do 'SHOW HOSTS' to check if storaged is activated

    def load_basketballplayer_dataset(self):
        udocker_command = (
            f"run --rm "
            f"vesoft/nebula-console:v3 "
            f"-addr {self.host} -port {self.port} -u root -p nebula -e ':play basketballplayer'"
        )
        self._run_udocker(udocker_command)
        time.sleep(10)

    def start_storaged(self):
        udocker_command = (
            f"run --rm --user=root -v "
            f"{self.base_path}/data/storage0:/data/storage -v "
            f"{self.base_path}/logs/storage0:/logs vesoft/nebula-storaged:v3 "
            f"--meta_server_addrs={self.host}:9559 --local_ip={self.host} "
            f"--ws_ip={self.host} --port=9779 --ws_http_port=19779 "
            f"--data_path=/data/storage --log_dir=/logs --v=0 --minloglevel=0"
        )
        if self._debug:
            print("starting storaged... with command:" f"\n{udocker_command}")

        self._run_udocker_background(udocker_command)
        time.sleep(20)
        if not self.on_colab:
            self._run_udocker_ps_filter("storaged")

    def start(self):
        self.udocker_init()
        self.start_metad()
        self.start_graphd()
        self.start_storaged()
        time.sleep(10)
        self.activate_storaged()
        time.sleep(20)
        print("loading basketballplayer dataset...")
        self.load_basketballplayer_dataset()
        print("nebulagraph_lite started successfully!")
        self.docker_ps()

    def check_status(self):
        self._run_udocker_ps_filter("metad")
        self._run_udocker_ps_filter("graphd")
        self._run_udocker_ps_filter("storaged")

    def docker_ps(self):
        return self._run_udocker("ps")

    def stop(self):
        if self.on_colab:
            self._run_udocker(
                "ps | grep nebula | awk '{print $1}' | xargs -I {} udocker rm {}"
            )
            return

        # in other environments, we cannot assume awk/xargs are installed
        # let's get the container ids first
        result = self._run_udocker("ps | grep nebula").stdout.decode()
        container_ids = [line.split()[0] for line in result.split("\n") if line]
        if container_ids:
            self._run_udocker(f"rm {' '.join(container_ids)}")
