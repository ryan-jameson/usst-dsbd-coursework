import struct
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PART_FILE = ROOT / "tmp" / "lecture_01_download_prefix.zip.part"
EXTRACT_DIR = ROOT / "tmp" / "lecture_01_prefix_extracted"


def main() -> None:
    data = PART_FILE.read_bytes()
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    offset = 0
    index = 0
    while offset + 30 <= len(data) and data[offset:offset + 4] == b"PK\x03\x04":
        index += 1
        (
            _signature,
            version,
            flags,
            method,
            _mtime,
            _mdate,
            crc32,
            compressed_size,
            uncompressed_size,
            name_length,
            extra_length,
        ) = struct.unpack_from("<IHHHHHIIIHH", data, offset)
        name_start = offset + 30
        name_end = name_start + name_length
        extra_end = name_end + extra_length
        name = data[name_start:name_end].decode("utf-8", errors="replace")
        print(
            f"entry={index} name={name!r} method={method} flags={flags} "
            f"header_comp={compressed_size} header_uncomp={uncompressed_size} crc={crc32:08x}"
        )

        if method != 8:
            print("unsupported_method_or_incomplete")
            break
        decompressor = zlib.decompressobj(-zlib.MAX_WBITS)
        payload = data[extra_end:]
        try:
            decompressed = decompressor.decompress(payload)
        except zlib.error as exc:
            print(f"decompress_error={exc}")
            break
        if not decompressor.eof:
            print(f"entry_incomplete_at_prefix bytes_available={len(payload)}")
            if name.lower().endswith(".mp4") and decompressed:
                output_path = EXTRACT_DIR / f"{Path(name).name}.part"
                output_path.write_bytes(decompressed)
                print(f"extracted_partial={output_path} bytes={len(decompressed)}")
            break

        consumed = len(payload) - len(decompressor.unused_data)
        descriptor_offset = extra_end + consumed
        if data[descriptor_offset:descriptor_offset + 4] == b"PK\x07\x08":
            descriptor_offset += 4
        if descriptor_offset + 12 > len(data):
            print("descriptor_incomplete")
            break
        desc_crc, desc_comp, desc_uncomp = struct.unpack_from("<III", data, descriptor_offset)
        print(
            f"entry_complete compressed={desc_comp} uncompressed={desc_uncomp} "
            f"descriptor_crc={desc_crc:08x}"
        )
        if desc_uncomp <= 2 * 1024 * 1024:
            output_name = Path(name).name
            output_path = EXTRACT_DIR / output_name
            output_path.write_bytes(decompressed)
            print(f"extracted={output_path}")
        offset = descriptor_offset + 12

    print(f"parsed_entries={index} parsed_bytes={offset} prefix_bytes={len(data)} next={data[offset:offset + 8].hex()}")


if __name__ == "__main__":
    main()
