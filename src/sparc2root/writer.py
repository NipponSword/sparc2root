import json

import numpy as np
import uproot

# dtype of each branch of the "frames" tree
FRAME_DTYPES = {
    "column": np.int16,
    "row": np.int16,
    "timestampSPARC": np.int32,     # 13 bit
    "timestampFPGA": np.uint64,     # 48 bit
    "fastor": np.int8,              # 1 = fast-OR word, 0 = pixel word
}


class Writer:
    def __init__(self, path):
        self._path = path

    def write(self, frames, regs=None, meta=None):
        """Write the frames dict (branch name -> list) to the TTree "frames".
        regs (BOR registers) and meta (EOR run metadata) are stored as JSON strings (TObjString)."""
        lengths = {len(v) for v in frames.values()}
        if len(lengths) > 1:
            raise ValueError(f"frames columns have different lengths: { {k: len(v) for k, v in frames.items()} }")

        branches = {k: np.asarray(v, dtype=FRAME_DTYPES.get(k)) for k, v in frames.items()}

        with uproot.recreate(self._path) as f:
            # mktree + extend writes a TTree. Assigning a dict (f["frames"] = ...) writes an RNTuple
            # in recent uproot, which older ROOT versions cannot read.
            tree = f.mktree("frames", {k: v.dtype for k, v in branches.items()})
            tree.extend(branches)
            if regs is not None:
                f["bor_registers"] = json.dumps(regs, default=str)
            if meta is not None:
                f["eor_metadata"] = json.dumps(meta, default=str)
