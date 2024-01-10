import os
import subprocess
import time
import functools
from typing import List, Type

LOCALHOST_V4 = "127.0.0.1"
DEFAULT_GRAPHD_PORT = 39669
BASE_PATH = os.path.expanduser("~/.nebulagraph/lite")


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
    ):
        self.host = host
        self.port = port
        self.base_path = base_path

        assert (
            os.path.expanduser("~") in self.base_path
        ), "Base path must be under current user's home directory"

        self._python_bin_path = os.path.dirname(os.sys.executable)
        self._debug = debug

        self.create_nebulagraph_lite_folders()

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
        except Exception as e:
            print(e)
            raise Exception(
                "nebulagraph_lite folders creation failed, "
                "please check if you have the permission to create folders in "
                f"{self.base_path}"
            )

    @retry((Exception,), tries=5, delay=5, backoff=3)
    def _run_udocker(self, command: str):
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

    def _run_udocker_background(self, command: str):
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
        self._run_udocker_ps_filter("storaged")

    def start(self):
        self.udocker_init()
        os.chdir(self.base_path)
        self.start_metad()
        self.start_graphd()
        self.start_storaged()
        time.sleep(10)
        self.activate_storaged()

        print("nebulagraph_lite started successfully!")

    def check_status(self):
        self._run_udocker_ps_filter("metad")
        self._run_udocker_ps_filter("graphd")
        self._run_udocker_ps_filter("storaged")

    def docker_ps(self):
        self._run_udocker("ps")
