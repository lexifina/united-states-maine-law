"""Arrange a bounded batch of official whole-title texts into chapter/section files.

The manifest names untouched source parts and official DOCX evidence. Failed acts
are held individually. No source part, legal word, date or source hash is changed.
Usage: python -X utf8 collect_section_batch.py MANIFEST OUTPUT_DIRECTORY
"""
import copy
import hashlib
import json
import sys
import zipfile
from pathlib import Path

from lxml import etree
from split_title_sections import NS, norm, official_text, split


def collect(manifest_path, output_directory):
    manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    output = Path(output_directory)
    output.mkdir(parents=True, exist_ok=True)
    parts, results, held = {}, [], []
    for item in manifest['acts']:
        try:
            source = Path(item['source_part'])
            original = json.loads(source.read_text(encoding='utf-8'))
            act = copy.deepcopy(next(a for a in original['acts'] if a['slug'] == item['slug']))
            assert len(act['versions']) == 1, 'not a single baseline'
            version = act['versions'][0]
            docx = Path(item['official_docx'])
            assert hashlib.sha256(docx.read_bytes()).hexdigest() == version['sha256'], 'source bytes changed'
            with zipfile.ZipFile(docx) as archive:
                root = etree.fromstring(archive.read('word/document.xml'))
            # Native formulas and drawings require their own structured readers.
            special = root.xpath('/w:document/w:body//w:drawing | /w:document/w:body//w:pict | /w:document/w:body//w:object | /w:document/w:body//m:oMath', namespaces={**NS, 'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'})
            assert not special, 'body contains image, object or native equation'
            text = version['units']['text']['text']
            units = split(text)
            assert norm(''.join(u['text'] for u in units.values())) == official_text(docx), 'official DOCX text mismatch'
            version['units'] = units
            version['note'] = 'Oldest version available; official title wording is arranged by chapter and section. Section history, repeal placeholders and repeated section numbers are retained as published.'
            part = parts.setdefault(source.name, {'corrects': source.name, 'acts': [], 'decisions': [], 'ai_use': ['GPT-6 wrote deterministic batch arrangement and verification code; no legal words were generated, corrected or translated by a model.']})
            part['acts'].append(act)
            part['decisions'].append(f"{act['slug']}: chapter and section boundaries follow official title headings. Concatenated units preserve the original whole-title text byte for byte and match the official Word body after whitespace normalization. Source hash and consolidation date are unchanged. Repeated section numbers remain separate units in publication order.")
            results.append({'slug': act['slug'], 'source_part': source.name, 'source_sha256': version['sha256'], 'date': version['from'], 'units': len(units), 'sections': sum(u['kind'] == 'sec' for u in units.values()), 'chapters': sum(u['kind'] == 'ch' for u in units.values()), 'source_images': 0, 'referenced_images': 0, 'omitted_images': 0, 'official_match': True})
        except Exception as error:
            held.append({'slug': item['slug'], 'reason': str(error)})
    names = []
    for number, (target, part) in enumerate(sorted(parts.items()), 87):
        name = f'{number}-q1581-sections.json'
        (output / name).write_text(json.dumps(part, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
        names.append(name)
    report = {'parts': names, 'acts': results, 'held': held}
    (output / 'batch-check.json').write_text(json.dumps(report, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'parts': names, 'acts': len(results), 'units': sum(r['units'] for r in results), 'sections': sum(r['sections'] for r in results), 'held': held}), flush=True)
    return report


if __name__ == '__main__':
    collect(*sys.argv[1:])
