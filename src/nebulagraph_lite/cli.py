from argparse import ArgumentParser

from nebulagraph_lite.nebulagraph import NebulaGraphLet as nebulagraph_let
from nebulagraph_lite import __version__


def main():
    parser = ArgumentParser(
        description="NebulaGraph Lite, your goto Graph Dev Runner"
    )
    subparsers = parser.add_subparsers(dest="command")

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        dest="debug",
        help="Whether to run in debug mode",
    )
    parser.add_argument(
        "-c",
        "--container",
        action="store_true",
        dest="in_container",
        help="Run in side a container",
    )
    parser.add_argument(
        "-H",
        "--host",
        type=str,
        dest="host",
        help="Listening in a host IP, by default it's 127.0.0.1",
    )
    parser.add_argument(
        "-P",
        "--port",
        type=int,
        dest="port",
        help="Listening in a port, by default it's 9669",
    )
    parser.add_argument(
        "-b",
        "--base_path",
        type=str,
        default=None,
        dest="base_path",
        help="Base path, by default it's ~/.nebulagraph/lite on non-colab env",
    )

    start_parser = subparsers.add_parser("start")

    start_parser.add_argument(
        "-u",
        "--cleanup",
        action="store_true",
        dest="clean_up",
        help="Run cleanup of the NebulaGraph data first before starting",
    )

    subparsers.add_parser("stop")
    subparsers.add_parser("shutdown")
    subparsers.add_parser("version")
    subparsers.add_parser("cleanup")
    subparsers.add_parser("start_metad")
    subparsers.add_parser("start_graphd")
    subparsers.add_parser("start_storaged")
    # subparsers.add_parser("ps")

    args = parser.parse_args()

    debug = args.debug
    in_container = args.in_container
    host = args.host
    port = args.port
    base_path = args.base_path

    if args.command == "start":
        start_clean_up = args.clean_up
        args = {
            "debug": debug,
            "in_container": in_container,
            "host": host,
            "port": port,
            "base_path": base_path,
            "clean_up": start_clean_up,
        }
        # pop None values
        args = {k: v for k, v in args.items() if v is not None}

        n = nebulagraph_let(
            **args,
        )
        n.start(fresh=bool(start_clean_up))
    elif args.command == "stop":
        args = {
            "debug": debug,
            "in_container": in_container,
            "host": host,
            "port": port,
            "base_path": base_path,
        }
        # pop None values
        args = {k: v for k, v in args.items() if v is not None}
        n = nebulagraph_let(
            **args,
        )
        n.stop()
    elif args.command == "shutdown":
        n = nebulagraph_let(
            debug=debug,
            in_container=in_container,
            host=host,
            port=port,
            base_path=base_path,
        )
        n.shutdown()
    elif args.command == "cleanup":
        n = nebulagraph_let(
            debug=debug,
            in_container=in_container,
            host=host,
            port=port,
            base_path=base_path,
        )
        n.clean_up()
    elif args.command == "start_metad":
        n = nebulagraph_let(
            debug=debug,
            in_container=in_container,
            host=host,
            port=port,
            base_path=base_path,
        )
        n.start_metad()
    elif args.command == "start_graphd":
        n = nebulagraph_let(
            debug=debug,
            in_container=in_container,
            host=host,
            port=port,
            base_path=base_path,
        )
        n.start_graphd()
    elif args.command == "start_storaged":
        n = nebulagraph_let(
            debug=debug,
            in_container=in_container,
            host=host,
            port=port,
            base_path=base_path,
        )
        n.start_storaged()
    elif args.command == "version":
        print(__version__)
    #    elif args.command == "ps":
    #        n = nebulagraph_let(
    #            debug=debug,
    #            in_container=in_container,
    #            host=host,
    #            port=port,
    #            base_path=base_path,
    #        )
    #        n.print_docker_ps()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
