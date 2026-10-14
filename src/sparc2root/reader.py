from pathlib import Path

from razorbill.cnstlnmsgpack import FileUnpacker, UnpackResult
from razorbill.devices.sparc import SPARCHitFrame, SPARCBusyFrame

class Reader:
    def __init__(self, path):
        self.hits = []
        self._unpacker = FileUnpacker(
            path,
            self._on_data,
            self._on_bor,
            self._on_eor)
        
    def _on_bor(self, sender, bor, device_map):
        regs = bor.userTags["sparc"]["registers"]
        decoder, config = device_map["sparc"]
        decoder.configure(config)

    def _on_data(self, sender, device, data, frame, decoder):

        if isinstance(frame, SPARCHitFrame):
            pass
        for hit in decoder.process(frame):
            self.hits.append((hit.column, hit.row, hit.timestamp, hit.raw))

    def _on_eor(self, sender, eor):
        self.meta = eor.runMetadata

    def read(self):
        r = UnpackResult.UNPACKED
        while r == UnpackResult.UNPACKED:
            r = self._unpacker.unpack()
        return r

    def show(self):
        print(f"The number of hits : {len(self.hits)}")
        print(f"Initial 5 hits as reference")

        for i in range(5):
            print(self.hits[i])
        
if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    test_file_path = project_root / "tests" / "sample_data" / "test.msgpack"
    
    reader = Reader(test_file_path)
    reader.read()
    reader.show()