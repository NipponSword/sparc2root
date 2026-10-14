import argparse
from pathlib import Path

from .reader import Reader
from .writer import Writer


def main():
    ap = argparse.ArgumentParser(description="Dump SPARC frames of a .msgpack file to a ROOT file")
    ap.add_argument("input", type=Path, help=".msgpack file written by the MessagePackWriter satellite")
    ap.add_argument("-o", "--output", type=Path, help="output ROOT file (default: <input>.root)")
    a = ap.parse_args()

    output = a.output or a.input.with_suffix(".root")

    reader = Reader(a.input)
    reader.read()
    Writer(output).write(reader.frames, regs=reader.regs, meta=reader.meta)

    n_fastor = sum(reader.frames["fastor"])
    print(f"{a.input} -> {output}: {len(reader.frames['fastor'])} frames (fast-OR {n_fastor})")


if __name__ == "__main__":
    main()
