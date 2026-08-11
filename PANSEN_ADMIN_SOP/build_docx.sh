#!/usr/bin/env bash
# Rebuild the WOWTOP-styled SOP docx (+PDF) from the markdown source.
#
# Why the post-processing: pandoc 2.12 + the Word reference template produce a
# docx that Word renders fine but LibreOffice (our PDF engine) renders broken,
# because the reference template was missing pandoc's cell styles and pandoc
# omits <w:tblGrid> on some tables. We therefore:
#   1) use _ref_template.docx  (Pansen headers/footers + Compact/FirstParagraph/
#      BlockText/VerbatimChar style definitions baked in)
#   2) swap pandoc's generic "Table" style -> LightGrid-Accent2 (pink WOWTOP look)
#   3) inject an equal-width <w:tblGrid> into every table that lacks one
# Result renders correctly in BOTH Word and LibreOffice/PDF.
#
# Usage: ./build_docx.sh [SRC.md] [OUT.docx]
set -euo pipefail
cd "$(dirname "$0")"
SRC="${1:-PANSEN_VMS_Admin_SOP_EN.md}"
OUT="${2:-${SRC%.md}.docx}"
REF="${3:-_ref_template.docx}"
PDF="${OUT%.docx}.pdf"
TMP="$(mktemp -d)"
echo "Building $OUT from $SRC (ref: $REF)"
pandoc "$SRC" -o "$TMP/build.docx" --reference-doc="$REF"
mkdir "$TMP/x"; ( cd "$TMP/x" && unzip -oq ../build.docx )
python3 - "$TMP/x/word/document.xml" << 'PY'
import io,sys,re
p=sys.argv[1]; s=io.open(p,encoding="utf-8").read()
# 1) table style -> LightGrid-Accent2
n1=s.count('w:tblStyle w:val="Table"')
s=s.replace('w:tblStyle w:val="Table"','w:tblStyle w:val="LightGrid-Accent2"')
# 2) inject equal-width tblGrid where missing (LibreOffice needs it)
TOTAL=9360; added=[0]
def fix(m):
    tbl=m.group(0)
    if '<w:tblGrid>' in tbl: return tbl
    tr=re.search(r'<w:tr\b.*?</w:tr>', tbl, re.S)
    n=len(re.findall(r'<w:tc>', tr.group(0))) if tr else 0
    if not n: return tbl
    grid='<w:tblGrid>'+('<w:gridCol w:w="%d" />'%(TOTAL//n))*n+'</w:tblGrid>'
    added[0]+=1
    return re.sub(r'(</w:tblPr>)', r'\1'+grid, tbl, count=1)
s=re.sub(r'<w:tbl>.*?</w:tbl>', fix, s, flags=re.S)
io.open(p,"w",encoding="utf-8").write(s)
print(f"  tables: {n1} -> LightGrid-Accent2, tblGrid injected into {added[0]}")
PY
[ -f "$OUT" ] && cp "$OUT" "$OUT.bak"
( cd "$TMP/x" && zip -r -X -q ../out.docx . )
cp "$TMP/out.docx" "$OUT"
rm -rf "$TMP"
echo "Done: $OUT"
# PDF via LibreOffice headless
if command -v soffice >/dev/null 2>&1; then
  soffice --headless --convert-to pdf --outdir . "$OUT" >/dev/null 2>&1 && echo "Done: $PDF"
fi
