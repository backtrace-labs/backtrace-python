import platform
import re
import subprocess

from backtracepython.attributes.attribute_provider import AttributeProvider


class MachineIdAttributeProvider(AttributeProvider):
    commands = {
        "Windows": 'reg query "HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Cryptography" /v MachineGuid',
        "Darwin": "ioreg -rd1 -c IOPlatformExpertDevice",
        "Linux": "( cat /var/lib/dbus/machine-id /etc/machine-id 2> /dev/null || hostname ) | head -n 1 || :",
        "FreeBSD": "kenv -q smbios.system.uuid || sysctl -n kern.hostuuid",
    }

    def __init__(self):
        self.id = self.read_machine_id()

    def get(self):
        return {"guid": self.id}

    def read_machine_id(self):

        current_system = platform.system()
        if current_system == "Windows":
            uuid_pattern = re.compile(
                r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
                re.IGNORECASE,
            )
            result = self.execute(self.commands[current_system])
            return uuid_pattern.findall(result)[0]
        if current_system == "Linux" or current_system == "FreeBSD":
            pattern = r"\r+|\n+|\s+"
            result = self.execute(self.commands[current_system])
            return re.sub(pattern, "", result).lower()
        if current_system == "Darwin":
            result = self.execute(self.commands[current_system]).split(
                "IOPlatformUUID"
            )[1]
            return re.sub(r'=|\s+|"', "", result, flags=re.IGNORECASE)[:32]

    def execute(self, command):
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode("utf-8").strip()
