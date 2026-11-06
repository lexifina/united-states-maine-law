"""Maine Titles 9-A and 29-A: the two official whole-title Word publications that each hold one native Word (OMML)
formula, which the q-104 parser (w:t text only) would have dropped. Same rules as q-104's parse_job.py (one text unit per
title, every paragraph of the body before the Revisor's copyright disclaimer, whitespace collapsed, dated by the
disclaimer's "current through" date), except that an m:oMath element is written in place as linear text:

    m:r / m:t     its text as published
    m:f           numerator/denominator; either side in parentheses when it holds a space or an operator (+ - * / ^ =)
    m:d           the delimiters m:begChr/m:endChr (default "(" and ")") around its m:e parts, joined by m:sepChr (default "|")
    m:sSup        base^exponent, the exponent in parentheses when longer than one character
    m:sSub        base_subscript, likewise; m:sSubSup both
    m:rad         sqrt(x) or root(degree, x)
    m:nary        the operator character (default the integral sign) with _lower ^upper, then the operand
    anything else stops the build if it holds text (STRICT), so nothing is dropped silently

No word or symbol is added except those brackets and the ^ / _ markers. Source: the q-104 job's official downloads
(legislature.maine.gov/statutes/<t>/title<t>.docx, retrieved 2026-11-06; sha256 recorded per version).

    python -X utf8 parse_formula_titles.py <out part.json>
"""
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'gpt-workers' / 'jobs' / 'q-104' / 'evidence'
W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
NS = {'w': W}
FOOTER = 'The State of Maine claims a copyright in its codified statutes.'
DATE_RE = re.compile(r'current through ([A-Za-z]+) (\d{1,2}), (\d{4})')
TITLES = ['9-A', '29-A']
OPS = set(' +-*/^=')


def q(tag, ns=M):
    return '{%s}%s' % (ns, tag)


def kids(el, tag):
    return [c for c in el if c.tag == q(tag)]


def prop(el, pr, name, default):
    p = el.find(q(pr))
    if p is not None:
        c = p.find(q(name))
        if c is not None:
            return c.get(q('val'), '')
    return default


def bracketed(s):
    """True when s is one bracket group from its first to its last character."""
    if not (s.startswith('(') and s.endswith(')')):
        return False
    depth = 0
    for i, ch in enumerate(s):
        depth += ch == '('
        depth -= ch == ')'
        if depth == 0 and i < len(s) - 1:
            return False
    return True


def wrap(s, always=False):
    return '(' + s + ')' if (always or any(ch in OPS for ch in s)) and not bracketed(s) else s


def m(el):
    t = el.tag.split('}')[1] if el.tag.startswith('{' + M) else None
    if t in ('oMath', 'oMathPara', 'e', 'num', 'den', 'sup', 'sub', 'deg'):
        return ''.join(m(c) for c in el if not c.tag.endswith('Pr'))
    if t == 'r':
        return ''.join(x.text or '' for x in el.iter(q('t')))
    if t == 'f':
        return wrap(m(el.find(q('num')))) + '/' + wrap(m(el.find(q('den'))))
    if t == 'd':
        beg, end, sep = prop(el, 'dPr', 'begChr', '('), prop(el, 'dPr', 'endChr', ')'), prop(el, 'dPr', 'sepChr', '|')
        return beg + sep.join(m(e) for e in kids(el, 'e')) + end
    if t == 'sSup':
        s = m(el.find(q('sup')))
        return m(el.find(q('e'))) + '^' + (s if len(s) == 1 else wrap(s, True))
    if t == 'sSub':
        s = m(el.find(q('sub')))
        return m(el.find(q('e'))) + '_' + (s if len(s) == 1 else wrap(s, True))
    if t == 'sSubSup':
        return m(el.find(q('e'))) + '_' + wrap(m(el.find(q('sub'))), True) + '^' + wrap(m(el.find(q('sup'))), True)
    if t == 'rad':
        d = el.find(q('deg'))
        dt = m(d) if d is not None else ''
        return ('root(' + dt + ', ' if dt else 'sqrt(') + m(el.find(q('e'))) + ')'
    if t == 'nary':
        ch = prop(el, 'naryPr', 'chr', '∫')
        sub, sup = el.find(q('sub')), el.find(q('sup'))
        out = ch
        if sub is not None and m(sub):
            out += '_' + wrap(m(sub), True)
        if sup is not None and m(sup):
            out += '^' + wrap(m(sup), True)
        return out + ' ' + m(el.find(q('e')))
    if el.tag.endswith('Pr') or el.tag == q('ctrlPr'):
        return ''
    txt = ''.join(x.text or '' for x in el.iter() if x.tag in (q('t'), q('t', W)))
    if txt:
        raise SystemExit(f'STRICT: no rule for {el.tag} holding text {txt!r}')
    return ''


def ptext(p, formulas):
    out = []

    def walk(el):
        if el.tag in (q('oMath'), q('oMathPara')):
            s = m(el)
            formulas.append(s)
            out.append(s)
            return
        if el.tag == q('t', W):
            out.append(el.text or '')
        for c in el:
            walk(c)
    walk(p)
    return ' '.join(''.join(out).split())


def parse_title(title, name):
    path = SOURCE / f'title-{title}.docx'
    raw = path.read_bytes()
    with zipfile.ZipFile(path) as z:
        body = ET.fromstring(z.read('word/document.xml')).find('w:body', NS)
    formulas = []
    paragraphs = [ptext(p, formulas) for p in body.findall('.//w:p', NS)]
    fs = next(i for i, p in enumerate(paragraphs) if p.startswith(FOOTER))
    mm = DATE_RE.search('\n'.join(paragraphs[fs:]))
    date = datetime.strptime(' '.join(mm.groups()), '%B %d %Y').strftime('%Y-%m-%d')
    text = '\n'.join(p for p in paragraphs[:fs] if p) + '\n'
    slug = 'title-' + title.lower() + '-' + re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')[:40].rstrip('-')
    act = {'slug': slug, 'short': f'{title} M.R.S.', 'title': f'Maine Revised Statutes, Title {title}. {name}',
           'url': f'https://legislature.maine.gov/statutes/{title}/title{title}ch0sec0.html',
           'first_law': None, 'earlier_laws': [], 'versions': [{
               'from': date, 'source_url': f'https://legislature.maine.gov/statutes/{title}/title{title}.docx',
               'sha256': hashlib.sha256(raw).hexdigest(), 'units': {'text': {'label': f'Title {title}', 'kind': 'text', 'text': text}},
               'credits': {}, 'in_force_basis': f'The official title disclaimer states that the consolidated text is current through {date}; this is a baseline, not the original commencement date.',
               'text_as_of': date,
               'note': 'Oldest version available, one file for the complete title. Chapter headings, section history and repeal placeholders are retained as published. Its one Word equation is written as linear text (see the corpus decisions). The source disclaimer gives the consolidation date; it does not establish the commencement of each section.'}]}
    return act, formulas


def main(out):
    listing = dict(json.loads((SOURCE / 'official-titles.json').read_text('utf-8')))
    acts, report = [], {}
    for t in TITLES:
        name = re.sub(r'^TITLE\s+[0-9A-Za-z-]+:\s*', '', listing[t])
        act, formulas = parse_title(t, name)
        acts.append(act)
        report[t] = formulas
    part = {'acts': acts,
            'sources': [{'name': 'Maine Revised Statutes, official whole-title Word publications (Titles 9-A and 29-A)',
                         'url': 'https://legislature.maine.gov/statutes/', 'retrieved': '2026-11-06',
                         'licence': 'State of Maine claims copyright; republication requires the Revisor disclaimer.',
                         'notes': 'Current consolidated Titles 9-A and 29-A, complete text; each holds one Word equation.'}],
            'decisions': ['Titles 9-A and 29-A follow the other whole-title files (one text file per title, dated by the disclaimer\'s current-through date). '
                          'Each holds one native Word equation (OMML), written in place as linear text: a fraction as numerator/denominator '
                          '(a side holding a space or an operator in parentheses), a delimiter group inside its own brackets, a superscript as ^(...). '
                          'Only those brackets and the ^ mark are added; every letter, digit and operator is the publication\'s. '
                          'Formulas: ' + '; '.join(f'{t}: {f}' for t, fs in report.items() for f in fs) + '.'],
            'ai_use': ['none']}
    Path(out).write_text(json.dumps(part, ensure_ascii=False, indent=1, sort_keys=True) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
