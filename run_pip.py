import socket
_orig = socket.getaddrinfo
socket.getaddrinfo = lambda host, port, family=0, *args, **kwargs: _orig(host, port, socket.AF_INET if family == 0 else family, *args, **kwargs)

import sys
from pip._internal.cli.main import main

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
