import re

from backtracepython.attributes.attribute_provider import AttributeProvider


class LinuxMemoryAttributeProvider(AttributeProvider):
    memory_match = re.compile(r"^(.+):\s+(\d+)\s*(.+)?$")

    memory_parser = {
        "MemTotal": "system.memory.total",
        "MemFree": "system.memory.free",
        "MemAvailable": "system.memory.available",
        "Buffers": "system.memory.buffers",
        "Cached": "system.memory.cached",
        "SwapCached": "system.memory.swap.cached",
        "Active": "system.memory.active",
        "Inactive": "system.memory.inactive",
        "SwapTotal": "system.memory.swap.total",
        "SwapFree": "system.memory.swap.free",
        "Dirty": "system.memory.dirty",
        "Writeback": "system.memory.writeback",
        "Slab": "system.memory.slab",
        "VmallocTotal": "system.memory.vmalloc.total",
        "VmallocUsed": "system.memory.vmalloc.used",
        "VmallocChunk": "system.memory.vmalloc.chunk",
    }

    process_parser = {
        "nonvoluntary_ctxt_switches": {
            "parse": "int",
            "attr": "sched.cs.involuntary",
        },
        "voluntary_ctxt_switches": {
            "parse": "int",
            "attr": "sched.cs.voluntary",
        },
        "FDSize": {"parse": "int", "attr": "descriptor.count"},
        "FDSize": {"parse": "int", "attr": "descriptor.count"},
        "VmData": {"parse": "kb", "attr": "vm.data.size"},
        "VmLck": {"parse": "kb", "attr": "vm.locked.size"},
        "VmPTE": {"parse": "kb", "attr": "vm.pte.size"},
        "VmHWM": {"parse": "kb", "attr": "vm.rss.peak"},
        "VmRSS": {"parse": "kb", "attr": "vm.rss.size"},
        "VmLib": {"parse": "kb", "attr": "vm.shared.size"},
        "VmStk": {"parse": "kb", "attr": "vm.stack.size"},
        "VmSwap": {"parse": "kb", "attr": "vm.swap.size"},
        "VmPeak": {"parse": "kb", "attr": "vm.vma.peak"},
        "VmSize": {"parse": "kb", "attr": "vm.vma.size"},
    }

    def get(self):
        result = {}

        result.update(self.read_system_info())
        result.update(self.read_process_info())
        return result

    def read_system_info(self):
        result = {}
        with open("/proc/meminfo", "r") as mem_info:
            for line in mem_info:
                match = self.memory_match.match(line)
                if not match:
                    continue
                name = match.group(1)
                if not name in self.memory_parser:
                    continue
                attribute_name = self.memory_parser[name]
                value = int(match.group(2))
                unit = match.group(3)
                if unit == "kB":
                    value *= 1024
                result[attribute_name] = value
        return result

    def read_process_info(self):
        result = {}
        with open("/proc/self/status", "r") as process_info:
            for line in process_info:
                value = line.split(":")
                attribute_key = value[0]
                if not attribute_key in self.process_parser:
                    continue

                parser = self.process_parser[attribute_key]
                attribute_value = int(value[1].strip().split(" ")[0])

                if parser["parse"] == "kb":
                    attribute_value *= 1024
                result[parser["attr"]] = attribute_value
        return result
