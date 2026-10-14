# sparc2root

Dump SPARC frames from a `.msgpack` file (Constellation MessagePackWriter) to a ROOT file, using razorbill for decoding.

## Install

razorbill is expected next to this repository (`../razorbill`, see `[tool.uv.sources]` in `pyproject.toml`).

```sh
uv sync
```

## Usage

```sh
uv run sparc2root run.msgpack            # writes run.root
uv run sparc2root run.msgpack -o out.root
```

## Output

- TTree `frames`: one entry per SPARC hit frame (pixel and fast-OR words)
  - `column`, `row` (int16): for fast-OR words (`fastor == 1`) these are the previously read address, not a position
  - `timestampSPARC` (int32, 13 bit), `timestampFPGA` (uint64, 48 bit)
  - `fastor` (int8): 1 = fast-OR word, 0 = pixel word
- `bor_registers`, `eor_metadata` (TObjString): BOR register values and EOR run metadata as JSON

Hitmap in ROOT: `frames->Draw("row:column", "fastor==0", "colz")`
