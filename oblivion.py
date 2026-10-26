
#!/usr/bin/env python3

import argparse
import os
import secrets
import sys
from pathlib import Path

MAGIC = b"OBLIVION-LK1"
MIN_KEY_BITS = 1_000_001
CHUNK_SIZE = 1024 * 1024


def write_new(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def generate_key(path, bits):
    if bits < MIN_KEY_BITS:
        raise ValueError(f"Key must contain at least {MIN_KEY_BITS} bits.")

    size = (bits + 7) // 8
    with open(path, "xb") as f:
        remaining = size
        while remaining:
            block = secrets.token_bytes(min(CHUNK_SIZE, remaining))
            f.write(block)
            remaining -= len(block)

    print(f"Generated {size * 8:,}-bit key: {path}")


def transform_chunk(data, key, nonce, offset):
    """
    Experimental large-key transformation.

    Every key byte contributes to the evolving state. This is a research
    construction, not a cryptographically validated encryption algorithm.
    """
    state = bytearray(key)
    key_len = len(state)

    for i, value in enumerate(nonce):
        j = (i * 131 + value) % key_len
        state[j] ^= value

    output = bytearray(len(data))

    for i, value in enumerate(data):
        pos = (offset + i) % key_len
        a = state[pos]
        b = state[(pos + 1) % key_len]
        c = state[(pos + key_len // 2) % key_len]

        mixed = (a + ((b << 1) | (b >> 7)) + c + pos) & 0xFF
        output[i] = value ^ mixed

        state[pos] = (
            (state[pos] ^ value ^ mixed) + b + 1
        ) & 0xFF

    return bytes(output)


def encrypt(input_path, output_path, key_path):
    key = Path(key_path).read_bytes()
    if len(key) * 8 < MIN_KEY_BITS:
        raise ValueError("Key is too short.")

    nonce = secrets.token_bytes(32)

    with open(input_path, "rb") as src:
        data = src.read()

    ciphertext = transform_chunk(data, key, nonce, 0)

    with open(output_path, "xb") as dst:
        dst.write(MAGIC)
        dst.write(nonce)
        dst.write(ciphertext)

    print(f"Encrypted {len(data):,} bytes to {output_path}")


def decrypt(input_path, output_path, key_path):
    key = Path(key_path).read_bytes()
    if len(key) * 8 < MIN_KEY_BITS:
        raise ValueError("Key is too short.")

    with open(input_path, "rb") as src:
        content = src.read()

    header_len = len(MAGIC)
    if content[:header_len] != MAGIC:
        raise ValueError("Invalid OBLIVION file.")

    nonce_start = header_len
    nonce_end = nonce_start + 32
    nonce = content[nonce_start:nonce_end]
    ciphertext = content[nonce_end:]

    plaintext = transform_chunk(ciphertext, key, nonce, 0)

    with open(output_path, "xb") as dst:
        dst.write(plaintext)

    print(f"Decrypted {len(plaintext):,} bytes to {output_path}")


def main():
    parser = argparse.ArgumentParser(prog="oblivion")
    sub = parser.add_subparsers(dest="cmd", required=True)

    kg = sub.add_parser("keygen")
    kg.add_argument("--bits", type=int, default=1_048_576)
    kg.add_argument("--output", required=True)

    enc = sub.add_parser("encrypt")
    enc.add_argument("input")
    enc.add_argument("output")
    enc.add_argument("--key", required=True)

    dec = sub.add_parser("decrypt")
    dec.add_argument("input")
    dec.add_argument("output")
    dec.add_argument("--key", required=True)

    args = parser.parse_args()

    try:
        if args.cmd == "keygen":
            generate_key(args.output, args.bits)
        elif args.cmd == "encrypt":
            encrypt(args.input, args.output, args.key)
        elif args.cmd == "decrypt":
            decrypt(args.input, args.output, args.key)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


