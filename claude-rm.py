#!/usr/bin/env python3
"""Pick Claude Code conversations with fzf and delete them.

Usage: claude-rm            pick sessions from every project
       claude-rm PATTERN    prefill the fzf query with PATTERN

Tab selects several sessions. Deletion asks for confirmation and cannot be undone.
The picker reopens after each round until Esc closes it.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.home() / ".claude"
PROJECTS = ROOT / "projects"


def records(path):
    with open(path, errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def prompts(path):
    """Yield the text of user-typed prompts, skipping meta and tool-result records."""
    for r in records(path):
        if r.get("type") == "user" and not r.get("isMeta"):
            content = r.get("message", {}).get("content")
            if isinstance(content, str) and not content.startswith("<"):
                yield content


def title(path):
    """Return the latest user-set name, else the latest generated title, else the first prompt."""
    custom = ai = None
    for r in records(path):
        if r.get("type") == "custom-title":
            custom = r.get("customTitle")
        elif r.get("type") == "ai-title":
            ai = r.get("aiTitle")
    return custom or ai or next(prompts(path), "(no prompt)")


def preview(path):
    p = Path(path)
    print(p.parent.name, p.stem, sep="\n", end="\n\n")
    for i, text in enumerate(prompts(p)):
        if i == 8:
            break
        print("> " + text.strip()[:400], end="\n\n")


def rows():
    files = sorted(PROJECTS.glob("*/*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in files:
        date = time.strftime("%Y-%m-%d %H:%M", time.localtime(p.stat().st_mtime))
        name = " ".join(title(p).split())[:100]
        yield f"{p}\t{date}  {p.parent.name}  {name}"


def main():
    query = sys.argv[1] if len(sys.argv) > 1 else ""
    # Reopen the picker after each round so several deletions need one launch; Esc exits.
    while True:
        picked = subprocess.run(
            ["fzf", "--multi", "--delimiter=\t", "--with-nth=2", f"--query={query}",
             f"--preview={sys.executable} {__file__} --preview {{1}}", "--preview-window=down:50%:wrap",
             "--header=Tab: select  Enter: delete selected  Esc: quit"],
            input="\n".join(rows()), stdout=subprocess.PIPE, text=True,
        ).stdout.splitlines()
        if not picked:
            return

        targets = [Path(line.split("\t", 1)[0]) for line in picked]
        for line in picked:
            print(line.split("\t", 1)[1])
        if input(f"Permanently delete {len(targets)} session(s)? [y/N] ").strip().lower() != "y":
            continue
        for p in targets:
            p.unlink(missing_ok=True)
            # Subagent transcripts and file edit history live beside the transcript, keyed by session ID.
            for extra in (p.with_suffix(""), ROOT / "file-history" / p.stem):
                shutil.rmtree(extra, ignore_errors=True)
        print(f"Deleted {len(targets)} session(s).")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--preview":
        preview(sys.argv[2])
    else:
        main()
