import warnings
from pathlib import Path

from razorbill.cnstlnmsgpack import FileUnpacker, UnpackResult
from razorbill.devices.sparc import SPARCHitFrame, SPARCBusyFrame

class Reader:
    def __init__(self, path):
        self.meta = None
        self.regs = None
        self.frames = {
            "column": [],
            "row": [],
            "timestampSPARC": [],
            "timestampFPGA" : [],
            "fastor": []
            }
        self._path = path
        self._unpacker = FileUnpacker(
            str(path),
            self._on_data,
            self._on_bor,
            self._on_eor)
        
    def _on_bor(self, sender, bor, device_map):
        regs = bor.userTags["sparc"]["registers"]
        self.regs = regs
        decoder, config = device_map["sparc"]

        config.set("tot_mode", regs["conf_tot_disable"] == 0)
        config.set("use_fast_or_timestamp", False)

        decoder.configure(config)

    def _on_data(self, sender, device, data, frame, decoder):
        if isinstance(frame, SPARCHitFrame):
            self.frames["column"].append(frame.column)
            self.frames["row"].append(frame.row)
            self.frames["timestampSPARC"].append(frame.timestampSPARC)
            self.frames["timestampFPGA"].append(frame.timestampFPGA)
            self.frames["fastor"].append(int(frame.fastOR)) 

    def _on_eor(self, sender, eor):
        self.meta = eor.runMetadata

    def read(self):
        r = UnpackResult.UNPACKED
        while r == UnpackResult.UNPACKED:
            r = self._unpacker.unpack()

        if r == UnpackResult.WAITING_FOR_DATA:
            warnings.warn(f"{self._path}: unpack ended with {r.name}")
        if r == UnpackResult.FAILED:
            raise RuntimeError(f"{self._path}: unpack failed")

        return r

    def show(self):
        n = len(self.frames["fastor"])
        print(f"The number of frames : {n}")
        print(f"Initial 5 frames as reference")

        for i in range(min(5, n)):
            print(
                self.frames["column"][i],
                self.frames["row"][i],
                self.frames["timestampSPARC"][i],
                self.frames["timestampFPGA"][i],
                self.frames["fastor"][i]
            )
        
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    test_file_path = project_root / "tests" / "sample_data" / "test.msgpack"
    
    reader = Reader(test_file_path)
    reader.read()
    reader.show()