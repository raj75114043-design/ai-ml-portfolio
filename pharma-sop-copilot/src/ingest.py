"""Section-aware chunking: every '## ' heading in an SOP becomes one retrievable chunk."""
import re
from pathlib import Path

SOP_DIR = Path(__file__).resolve().parent.parent / "data" / "sops"


def load_chunks(sop_dir=SOP_DIR):
    chunks = []
    for path in sorted(Path(sop_dir).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        header = text.splitlines()[0].lstrip("# ").strip()
        sop_id, title = [p.strip() for p in header.split("—", 1)]
        for section in re.split(r"\n(?=## )", text)[1:]:
            heading, _, body = section.partition("\n")
            heading = heading.lstrip("# ").strip()
            num = heading.split(".")[0]
            chunks.append({
                "id": f"{sop_id} §{num}",
                "sop_id": sop_id,
                "sop_title": title,
                "section": heading,
                "text": f"{title}. {heading}. {body.strip()}",
                "body": body.strip(),
            })
    return chunks
