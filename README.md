
# OBLIVION-LK1

Experimental large-key encryption research in Python.

OBLIVION-LK1 explores a custom state-based encryption design that accepts key material exceeding one million bits. The project provides a command-line interface for generating large random keys and experimenting with file encryption and decryption.

## Features

- Generates random keys exceeding 1,000,000 bits.
- Supports file encryption and decryption.
- Uses a custom state-based transformation.
- Runs with Python 3 and the standard library.
- Requires no external cryptography packages.

## Requirements

- Python 3.10 or newer
- Linux, macOS, or Windows

## Usage

### Generate a key

Generate a key containing 1,048,576 bits:

```bash
python3 oblivion.py keygen \
  --bits 1048576 \
  --output oblivion.key
```

Generate a key with 1,000,008 bits:

```bash
python3 oblivion.py keygen \
  --bits 1000001 \
  --output oblivion.key
```

Keys are stored as binary files. Because files contain whole bytes, the second command produces 1,000,008 bits of key material.

### Encrypt a file

```bash
python3 oblivion.py encrypt input.bin encrypted.obl \
  --key oblivion.key
```

### Decrypt a file

```bash
python3 oblivion.py decrypt encrypted.obl recovered.bin \
  --key oblivion.key
```

The output filename must not already exist.

## Technical Overview

OBLIVION-LK1 uses a custom state-based transformation rather than AES or a one-time pad.

The implementation accepts large keys and uses their bytes as an evolving internal state. The key's size alone does not establish the algorithm's effective security.



## Contributing

Ideas, code review, testing, and cryptanalysis feedback are welcome. Security claims should be supported by reproducible testing and rigorous analysis.

