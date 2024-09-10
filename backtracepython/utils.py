import platform
import sys

python_version = "{} {}.{}.{}-{}".format(
    platform.python_implementation(),
    sys.version_info.major,
    sys.version_info.minor,
    sys.version_info.micro,
    sys.version_info.releaselevel,
)


def get_python_version():
    return python_version
