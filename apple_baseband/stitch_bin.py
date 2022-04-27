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


def main():
    parser = argparse.ArgumentParser(description='Create a flat binary from the Qualcomm MBN')
    parser.add_argument('input_file',
                        help='The path to the input Qualcomm MBN binary')

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"{args.input_file} is not a regular file")
        exit(-1)

    mbn_path = pathlib.Path(args.input_file)
    stitch_bin_from_mbn(mbn_path.expanduser())


def stitch_bin_from_mbn(input_file: pathlib.Path):
    elf_structs = elftools.elf.structs.ELFStructs()
    elf_structs.create_basic_structs()
    elf_structs.create_advanced_structs()
    header_entries = []

    with input_file.open('rb') as input_stream:
        elf_header = elftools.common.utils.struct_parse(elf_structs.Elf_Ehdr, input_stream, stream_pos=0)
        logging.info(f"[+] Found %d program headers {elf_header.e_phnum}")
        for header_index in range(elf_header.e_phnum):
            header_entries.append(elftools.common.utils.struct_parse(elf_structs.Elf_Phdr, input_stream))

        # The first two entries are the ELF headers and the Qualcomm signatures
        header_entries = header_entries[2:]
        header_entries = [entry for entry in header_entries if entry.p_filesz != 0]
        minimum_offset = min([entry.p_vaddr for entry in header_entries])
        with input_file.with_suffix('.bin').open('wb') as output_file:
            for entry in header_entries:
                memory_from_base = entry.p_vaddr - minimum_offset
                region_end = memory_from_base + entry.p_memsz
                output_file.seek(memory_from_base)
                input_stream.seek(entry.p_offset)
                output_file.write(input_stream.read(entry.p_filesz))
                output_file.seek(region_end)


if __name__ == "__main__":
    main()
