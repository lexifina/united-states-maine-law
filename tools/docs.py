"""Maine: write repo/README.md, LICENSE, jurisdiction.json."""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'world-law'))
import us_state_lib as L

c = json.loads((HERE / 'corpus.json').read_text('utf-8'))
n = {a['slug']: len(a['versions'][0]['units']) for a in c['acts']}

DISCLAIMER = ("All copyrights and other rights to statutory text are reserved by the State of Maine. The text included in this publication "
              "reflects changes made through the Second Regular Session of the 132nd Maine Legislature and is current through October 1, 2026. "
              "The text is subject to change without notice. It is a version that has not been officially certified by the Secretary of State. "
              "Refer to the Maine Revised Statutes Annotated and supplements for certified text.")

README = f"""# Maine: law history in git

The Constitution of Maine and three core titles of the Maine Revised Statutes as a git repository: one file per provision, one paragraph per line, so `git blame` works line by line. It follows the shared design of [lexifina/global-law](https://github.com/lexifina/global-law).

**What is in it now**

| Folder | Act | Versions | History |
| --- | --- | ---: | --- |
| `constitution/` | Constitution of the State of Maine, 2023 arrangement ({n['constitution']} sections) | 1 | Oldest version available, dated 16 January 2024 |
| `criminal-code/` | Title 17-A, Maine Criminal Code ({n['criminal-code']} sections) | 1 | Oldest version available, current through 1 October 2026 |
| `property/` | Title 33, Property ({n['property']} sections) | 1 | Same |
| `business-corporation-act/` | Title 13-C, Maine Business Corporation Act ({n['business-corporation-act']} sections) | 1 | Same |

That is all the law this repository holds today. The other titles, session laws and rules are not in it.

## Where the text comes from

The statutes are the Maine Revised Statutes as published online by the Office of the Revisor of Statutes (<https://legislature.maine.gov/statutes/>), one page per section. The Constitution is the Revisor's PDF of the arrangement approved by Resolve 2023, chapter 86 (<https://legislature.maine.gov/doc/10674>), which includes CR 2023, chapters 1 and 2.

The State of Maine claims a copyright in its codified statutes and asks republishers to include this disclaimer, which is reproduced here as the Revisor requires:

> {DISCLAIMER}

The Revisor also asks to be sent one copy of any statutory publication; the Revisor of Statutes is the contact for that.

## Dates

- Each statute title is one version, dated **1 October 2026**, the date the Revisor states the text is current through. It is the oldest version available: the Revisor publishes no earlier text online in this form.
- The Constitution is dated **16 January 2024**, the creation date of the Revisor's PDF, because the PDF gives no in-force date.
- The first commit of each act is credited to the publisher as "oldest version available".

## What it does not show

- Any history before these dates. The bracketed session-law notes after each subsection (for example "PL 2011, c. 274, §1 (AMD)") name the laws behind the text but are not copied.
- Repealed, reallocated and renumbered sections (they carry no text).
- Titles other than 13-C, 17-A and 33, and amendments passed after 1 October 2026.
- In the Constitution, a section's heading and first paragraph run on one line, as printed; page headers and the Revisor's section-history notes are left out.
- Nothing here is an official publication or legal advice.

## How it is checked

- Every unit is read back from git on its day and compared with the corpus (`tools/check_repo.py`; results in `REPRODUCE.md`).
- The sources are identified by their sha256, in `data/versions.json`.
"""

LICENSE = f"""The legal texts are the Constitution of Maine and the Maine Revised Statutes (Titles 13-C, 17-A and 33) as published by the Office of
the Revisor of Statutes, Maine Legislature, at https://legislature.maine.gov/statutes/ and https://legislature.maine.gov/doc/10674.

The State of Maine claims a copyright in its codified statutes and requires that republications include the following disclaimer.
It is reproduced here exactly as the Revisor publishes it at the foot of every statute page:

  {DISCLAIMER}

The Revisor also requests that one copy of any statutory publication be sent to the Office of the Revisor of Statutes.
(Statutes are edicts of government that United States copyright law does not protect; this repository nevertheless complies with the Revisor's stated condition.)

Changes made by Lexifina: one Markdown file per section, one paragraph per line, normalised spaces, quotation marks and hyphens, bracketed
session-law history notes and repealed sections left out. The wording of the law was not changed. The Revisor of Statutes does not endorse
this repository.

Lexifina's own contributions (the arrangement of the history, the commit messages, the tables and the tools) are dedicated to the
public domain under CC0 1.0 Universal: https://creativecommons.org/publicdomain/zero/1.0/legalcode
"""

L.write_repo(HERE, README, LICENSE, {
    'path': 'us-me', 'code': 'ME', 'name': 'Maine', 'level': 'state',
    'repo': 'https://github.com/lexifina/united-states-maine-law',
    'build': 'built: Constitution and Maine Revised Statutes Titles 13-C, 17-A and 33, one version each (statutes current through 2026-10-01)',
    'register_date': '2026-10-30'})
