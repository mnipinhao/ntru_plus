#!/usr/bin/env python3
"""Stage exact P50 baseline and parameterized GT768 NO_CE hash_g candidate."""

from __future__ import annotations

import hashlib
import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BUILD = HERE / "build"
SYNC = BUILD / "sync"
PRODUCTION = Path("ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864")
BASELINE_REVISION = "03f8ba296666cdb96d143816e676ea625fc428da"
REFERENCE_REVISION = "631274d51bd4ce488bebbaef9f5d7f92a1e2b8d9"
REFERENCE_ASM = "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768/keccakf1600.S"


def extract(destination: Path) -> None:
    archive = subprocess.check_output(
        ["git", "archive", BASELINE_REVISION, str(PRODUCTION)], cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream.getmembers():
            if not member.isfile():
                continue
            relative = Path(member.name).relative_to(PRODUCTION)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            source = stream.extractfile(member)
            assert source is not None
            target.write_bytes(source.read())


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"P53 anchor drift for {label}: {text.count(old)}")
    return text.replace(old, new)


def adapt_assembly() -> str:
    text = subprocess.check_output(
        ["git", "show", f"{REFERENCE_REVISION}:{REFERENCE_ASM}"],
        cwd=ROOT, text=True)
    text = replace_once(text,
        "/* Fixed hash_g: x0=out[192], x1=msg[1152], x2=rc[24].",
        "/* Fixed hash_g: x0=out[216], x1=msg[1296], x2=rc[24].",
        "fixed signature")
    text = replace_once(text,
        "cmp x0, #8\n        b.lo Lhash_g_full\n        b.eq Lhash_g_tail\n        cmp x0, #9",
        "cmp x0, #9\n        b.lo Lhash_g_full\n        b.eq Lhash_g_tail\n        cmp x0, #10",
        "block count")
    text = replace_once(text,
        "        ldrb w26, [x0, #64]\n        orr x26, x26, #0x1f00\n        eor x17, x17, x26",
        "        ldr x26, [x0, #64]\n        eor x17, x17, x26\n"
        "        ldrb w26, [x0, #72]\n        orr x26, x26, #0x1f00\n        eor x22, x22, x26",
        "73-byte tail")
    text = replace_once(text,
        "        mov x26, #9\n        str x26, [sp, #136]\n"
        "        b Lhash_g_live_round\n\nLhash_g_squeeze_first:",
        "        mov x26, #10\n        str x26, [sp, #136]\n"
        "        b Lhash_g_live_round\n\nLhash_g_squeeze_first:",
        "tail next state")
    text = replace_once(text,
        "        mov x26, #10\n        str x26, [sp, #136]\n"
        "        b Lhash_g_live_round\n\nLhash_g_squeeze_last:",
        "        mov x26, #11\n        str x26, [sp, #136]\n"
        "        b Lhash_g_live_round\n\nLhash_g_squeeze_last:",
        "squeeze next state")
    text = replace_once(text,
        "        stp x21, x2, [x0, #32]\n        str x7, [x0, #48]",
        "        stp x21, x2, [x0, #32]\n"
        "        stp x7, x12, [x0, #48]\n"
        "        stp x17, x22, [x0, #64]",
        "80-byte final squeeze")
    return text


def update_manifest(package: Path, extras: list[str]) -> None:
    manifest = package / "SOURCE-MANIFEST.sha256"
    names = [line.split(None, 1)[1] for line in manifest.read_text().splitlines()
             if line.strip()]
    for name in extras:
        if name not in names:
            names.append(name)
    manifest.write_text("".join(
        f"{hashlib.sha256((package / name).read_bytes()).hexdigest()}  {name}\n"
        for name in names))


def main() -> None:
    if SYNC.exists():
        shutil.rmtree(SYNC)
    for name in ("baseline", "candidate"):
        extract(SYNC / "packages" / name)
    candidate = SYNC / "packages/candidate"
    (candidate / "gt864_p53_keccakf1600.S").write_text(adapt_assembly())
    shutil.copy2(HERE / "hash-g-fixed.c", candidate / "gt864_p53_hash_g_fixed.c")

    symmetric = candidate / "symmetric.c"
    text = symmetric.read_text()
    text = replace_once(text,
        "void gt864_p18_tobytes_full_asm(uint8_t *, const int16_t *);",
        "void gt864_p18_tobytes_full_asm(uint8_t *, const int16_t *);\n"
        "void gt864_p53_hash_g_fixed(uint8_t output[216], const uint8_t input[1296]);",
        "fixed hash declaration")
    old_hash_g = """void hash_g(uint8_t *buf, const uint8_t *msg)
{
    uint8_t data[1 + HASH_G_INBYTES];

    data[0] = 0x01;
    memcpy(data + 1, msg, HASH_G_INBYTES);
    shake256(buf, HASH_G_OUTBYTES, data, HASH_G_INBYTES + 1);
}"""
    new_hash_g = """void hash_g(uint8_t *buf, const uint8_t *msg)
{
    gt864_p53_hash_g_fixed(buf, msg);
}"""
    text = replace_once(text, old_hash_g, new_hash_g, "hash_g")
    old_fr0 = """    uint8_t data[1 + HASH_G_INBYTES];

    data[0] = 0x01;
    gt864_p18_tobytes_full_asm(data + 1, coeffs);
    shake256(buf, HASH_G_OUTBYTES, data, HASH_G_INBYTES + 1);"""
    new_fr0 = """    uint8_t data[HASH_G_INBYTES];

    gt864_p18_tobytes_full_asm(data, coeffs);
    gt864_p53_hash_g_fixed(buf, data);"""
    symmetric.write_text(replace_once(text, old_fr0, new_fr0, "hash_g_fr0"))

    makefile = candidate / "Makefile"
    text = makefile.read_text()
    anchor = "NATIVE_OBJECTS += gt864_p35_inverse16_ternary.o gt864_p35_inverse_tail_ternary.o\n"
    addition = (anchor + "HASH_OBJECTS := gt864_p53_hash_g_fixed.o gt864_p53_keccakf1600.o\n"
                "gt864_p53_hash_g_fixed.o: gt864_p53_hash_g_fixed.c\n"
                "\t$(CC) $(CFLAGS) -I. -c $< -o $@\n"
                "gt864_p53_keccakf1600.o: gt864_p53_keccakf1600.S\n"
                "\t$(CC) $(CFLAGS) -I. -x assembler-with-cpp -c $< -o $@\n")
    text = replace_once(text, anchor, addition, "Makefile objects")
    text = text.replace("$(TOBYTES_OBJECTS) $(NATIVE_OBJECTS)",
                        "$(TOBYTES_OBJECTS) $(NATIVE_OBJECTS) $(HASH_OBJECTS)")
    makefile.write_text(text)
    update_manifest(candidate, ["gt864_p53_hash_g_fixed.c", "gt864_p53_keccakf1600.S"])

    shutil.copy2(HERE / "test-hash.c", SYNC / "test-hash.c")
    source_manifest = {
        str(path.relative_to(SYNC)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(SYNC.rglob("*")) if path.is_file()
    }
    (BUILD / "source-manifest.json").write_text(json.dumps({
        "experiment": "GT864-P53-NOCE-HASH-G-20260916",
        "baseline_revision": BASELINE_REVISION,
        "reference_revision": REFERENCE_REVISION,
        "reference_source": REFERENCE_ASM,
        "files": source_manifest,
    }, indent=2) + "\n")
    print(f"prepared P53 files={len(source_manifest)}")


if __name__ == "__main__":
    main()
