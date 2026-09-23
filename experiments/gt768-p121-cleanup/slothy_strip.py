"""P121: remove Slothy's schedule listings from an assembly file, keeping one
summary line per scheduled region.  Comments only (verified by comparing objects).

Dropped: the source-instruction listing and cycle diagram emitted after each region,
the per-instruction timing marks (`// ..*..`), and the three statistics lines, which
become `// Slothy schedule: N instructions, C cycles expected (IPC x)`.
usage: slothy_strip.py FILE"""
import re, sys
p = sys.argv[1]; out = []; stats = {}; dropped = 0
for line in open(p).read().split('\n'):
    s = line.strip()
    m = re.match(r'//\s*(Instructions|Expected cycles|Expected IPC):\s*(\S+)$', s)
    if m:
        stats[m.group(1)] = m.group(2); dropped += 1
        if len(stats) == 3:
            out.append(f"    // Slothy schedule: {stats['Instructions']} instructions, "
                       f"{stats['Expected cycles']} cycles expected (IPC {stats['Expected IPC']})")
            stats = {}
        continue
    if s.startswith('//') and (
            re.search(r'cycle \(expected\)', s) or re.fullmatch(r'//[\s0-9]*', s)
            or re.fullmatch(r'//\s*\|[-|]*', s)
            or re.fullmatch(r'//\s*\S.*?//\s*[.*]+', s)):          # listing: "// insn   // ..*.."
        dropped += 1; continue
    new = re.sub(r'\s*//\s*[.*]+\s*$', '', line) if not s.startswith('//') else line
    if new != line: dropped += 1
    out.append(new.rstrip())
text = re.sub(r'\n{3,}', '\n\n', '\n'.join(out))
open(p, 'w').write(text)
print(f'{p}: {dropped} comment lines/marks removed')
