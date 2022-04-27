#!/usr/bin/env python

# Adapted from https://github.com/laginimaineb/unify_trustlet

import sys
import os
import argparse
import struct
import logging
import pathlib
import elftools.common.utils
import elftools.elf.structs


class ELFWriter:
    def __init__(self, output_path: pathlib.Path, header_path: pathlib.Path):
        self._header_path = header_path.expanduser()
        self._output_path = output_path.expanduser()
        self._elf_structs = elftools.elf.structs.ELFStructs()
        self._elf_structs.create_basic_structs()
        self._elf_structs.create_advanced_structs()
        self._header_entries = []

    def __enter__(self):
        self._output_file = self._output_path.open('wb')
        with self._header_path.open('rb') as header:
            self._output_file.write(header.read())
            self._elf_header = elftools.common.utils.struct_parse(self._elf_structs.Elf_Ehdr, header, stream_pos=0)
            logging.info("[+] Found %d program headers" % self._elf_header.e_phnum)
            for header_index in range(self._elf_header.e_phnum):
                self._header_entries.append(elftools.common.utils.struct_parse(self._elf_structs.Elf_Phdr, header))

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._output_file:
            self._output_file.close()

    def write_file_to_location(self, file_path: pathlib.Path, offset: int):
        with file_path.open('rb') as chunk_file:
            self._output_file.seek(offset)
            self._output_file.write(chunk_file.read())

    @property
    def headers(self) -> list:
        return self._header_entries


def main():
    parser = argparse.ArgumentParser(description='Unify a Qualcomm MDT file-set into a ELF equivalent')
    parser.add_argument('input_file',
                        help='The path to the input Qualcomm MDT manifest')
    parser.add_argument('--output', dest='output_file', action='store', type=str,
                        help='The output file path (defaults to the <trustlet_name>.elf)')

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"{args.input_file} is not a regular file")
        exit(-1)

    mdt_path = pathlib.Path(args.input_file)
    output_file_path = pathlib.Path(args.output_file) or mdt_path.with_suffix('.elf')
    convert_to_elf(mdt_path, output_file_path)


def convert_to_elf(trustlet_manifest: pathlib.Path, output_file_path: pathlib.Path):
    # Reading each of the program headers and copying the relevant chunk
    with ELFWriter(output_file_path, trustlet_manifest) as output_file:
        for index, header in enumerate(output_file.headers):
            # Reading the PHDR
            print(f"[+] Reading PHDR {index:d}")
            print(f"[+] Size: 0x{header.p_filesz:08X}, Offset: 0x{header.p_offset:08X}")

            if header.p_filesz == 0:
                print("[+] Empty block, skipping")
                continue  # There's no backing block

            # Copying out the data in the block
            chunk_filename = trustlet_manifest.with_suffix(f".b{index:02d}")
            chunk_stat = chunk_filename.stat()
            if chunk_stat.st_size != header.p_filesz:
                logging.warning(f"[*] WARNING: chunk size is {chunk_stat.st_size} and header is {header.p_filesz}")
            output_file.write_file_to_location(chunk_filename, header.p_offset)


if __name__ == "__main__":
    main()
