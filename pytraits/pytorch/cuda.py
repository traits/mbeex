import torch


class Cuda:
    def __init__(self):
        self._device_count = 0
        self._device_names = []
        if self.hasCuda():
            self._device_count = torch.cuda.device_count()
            for i in range(self._device_count):
                self._device_names.append(torch.cuda.get_device_name(i))

    def hasCuda(self):
        return torch.cuda.is_available()

    def device_count(self):
        return self._device_count

    def device_names(self):
        return self._device_names

    def print_mem_info(self):
        """Get total memory of all devices."""

        capacities = [
            f"{torch.cuda.get_device_properties(i).total_memory/1024/1024/1024}GB"
            for i in range(self.device_count())
        ]
        print(f"memory: {list(zip(self.device_names(), capacities))}")


def info():
    cu = Cuda()
    # print("CUDNN VERSION:", torch.backends.cudnn.version())
    print(f"hasCuda(): {cu.hasCuda()}")
    print(f"Number of CUDA Devices: {cu.device_count()}")
    print(f"devices: {cu.device_names()}")
    cu.print_mem_info()
