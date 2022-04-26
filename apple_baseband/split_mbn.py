import sys
import os
import argparse
import struct
import logging
import pathlib
import elftools.common.utils
import elftools.elf.structs


def main():
    parser = argparse.ArgumentParser(description='Unify a Qualcomm MDT file-set into a ELF equivalent')
    parser.add_argument('input_file',
                        help='The path to the input Qualcomm MDT manifest')

    args = parser.parse_args()

    if not os.path.exists(args.input_file):
        print(f"{args.input_file} is not a regular file")
        exit(-1)

    mbn_path = pathlib.Path(args.input_file)
    split_mbn(mbn_path.expanduser())


def split_mbn(input_file: pathlib.Path):
    elf_structs = elftools.elf.structs.ELFStructs()
    elf_structs.create_basic_structs()
    elf_structs.create_advanced_structs()
    header_entries = []

    with input_file.open('rb') as input_stream:
        elf_header = elftools.common.utils.struct_parse(elf_structs.Elf_Ehdr, input_stream, stream_pos=0)
        logging.info(f"[+] Found %d program headers {elf_header.e_phnum}")
        for header_index in range(elf_header.e_phnum):
            header_entries.append(elftools.common.utils.struct_parse(elf_structs.Elf_Phdr, input_stream))

        for index, entry in enumerate(header_entries):
            input_stream.seek(entry.p_offset)
            with input_file.with_suffix(f".b{index:02d}").open('wb') as output_file:
                output_file.write(input_stream.read(entry.p_filesz))


if __name__ == "__main__":
    main()
