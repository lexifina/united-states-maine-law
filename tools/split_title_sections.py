"""Split a published whole-title act into source-checked chapter and section units.

Usage: python -X utf8 split_title_sections.py SOURCE_PART ACT_SLUG OFFICIAL_DOCX OUTPUT_PART
The output is a complete correction act. It never edits SOURCE_PART.
"""
import copy
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

from lxml import etree

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
FOOTER = 'The State of Maine claims a copyright in its codified statutes.'


def norm(value):
    return re.sub(r'\s+', ' ', value).strip()


def official_text(path):
    with zipfile.ZipFile(path) as archive:
        root = etree.fromstring(archive.read('word/document.xml'))
    lines = []
    for paragraph in root.xpath('/w:document/w:body//w:p', namespaces=NS):
        line = ''.join(paragraph.xpath('.//w:t/text()', namespaces=NS))
        if line.startswith(FOOTER):
            break
        lines.append(line)
    return norm('\n'.join(lines))


def split(text):
    chunks = []
    for line in text.splitlines(keepends=True):
        if re.match(r'^(?:CHAPTER\s+\S+|§\S+)', line):
            chunks.append([])
        if not chunks:
            chunks.append([])
        chunks[-1].append(line)
    units = {}
    for number, lines in enumerate(chunks, 1):
        body = ''.join(lines)
        heading = lines[0].strip()
        if heading.startswith('§'):
            kind = 'sec'
        elif heading.startswith('CHAPTER '):
            kind = 'ch'
        else:
            kind = 'text'
            heading = 'Title heading'
        units[f'unit-{number:04d}'] = {'kind': kind, 'label': heading, 'text': body}
    assert ''.join(unit['text'] for unit in units.values()) == text
    return units


def main(source_part, act_slug, source_docx, output_part):
    source_part, source_docx, output_part = map(Path, (source_part, source_docx, output_part))
    original = json.loads(source_part.read_text(encoding='utf-8'))
    act = copy.deepcopy(next(a for a in original['acts'] if a['slug'] == act_slug))
    assert len(act['versions']) == 1
    version = act['versions'][0]
    assert hashlib.sha256(source_docx.read_bytes()).hexdigest() == version['sha256']
    text = version['units']['text']['text']
    units = split(text)
    assert norm(''.join(unit['text'] for unit in units.values())) == official_text(source_docx)
    version['units'] = units
    version['note'] = 'Oldest version available; official title wording is arranged by chapter and section. Section history and repeal placeholders are retained as published.'
    part = {
        'corrects': source_part.name,
        'acts': [act],
        'decisions': [f'{act_slug}: chapter and section boundaries come from headings in the official Word document. The concatenated units equal the unchanged published title text byte for byte and match the official Word body after whitespace normalization. The version date and source hash are unchanged.'],
        'ai_use': ['GPT-6 wrote the deterministic section splitter; no legal words were generated, corrected or translated by a model.'],
    }
    output_part.write_text(json.dumps(part, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'units': len(units), 'sections': sum(u['kind'] == 'sec' for u in units.values()), 'chapters': sum(u['kind'] == 'ch' for u in units.values()), 'official_sha256': version['sha256'], 'official_match': True, 'unchanged_published_text': True}))


if __name__ == '__main__':
    main(*sys.argv[1:])
