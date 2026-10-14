import json

import numpy as np
import pytest
import uproot

from sparc2root.writer import Writer


def make_frames():
    return {
        "column": [17, 17, 3],
        "row": [18, 18, 5],
        "timestampSPARC": [100, 8191, 0],
        "timestampFPGA": [2**47 + 1, 5, 0],
        "fastor": [0, 1, 0],
    }


def test_write_frames(tmp_path):
    out = tmp_path / "out.root"
    Writer(out).write(make_frames(), regs={"conf_tot_disable": 1}, meta={"condition": "test"})

    with uproot.open(out) as f:
        t = f["frames"]
        assert t.num_entries == 3
        a = t.arrays(library="np")
        assert a["column"].dtype == np.int16
        assert a["timestampFPGA"].dtype == np.uint64
        assert a["timestampFPGA"][0] == 2**47 + 1
        assert list(a["fastor"]) == [0, 1, 0]
        assert json.loads(str(f["bor_registers"])) == {"conf_tot_disable": 1}
        assert json.loads(str(f["eor_metadata"])) == {"condition": "test"}


def test_write_empty(tmp_path):
    out = tmp_path / "empty.root"
    Writer(out).write({k: [] for k in make_frames()})
    with uproot.open(out) as f:
        assert f["frames"].num_entries == 0
        assert "bor_registers" not in f


def test_length_mismatch(tmp_path):
    frames = make_frames()
    frames["row"].pop()
    with pytest.raises(ValueError):
        Writer(tmp_path / "bad.root").write(frames)
