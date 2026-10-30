# How this repository was made (Maine)

This file is written by the build on 2026-10-30, the day the source data was retrieved.

## Sources

| Source | Address | Retrieved | Licence |
| --- | --- | --- | --- |
| Maine Revised Statutes (Office of the Revisor of Statutes) | <https://legislature.maine.gov/statutes/> | 2026-10-30 | State of Maine claims copyright; republication requires the disclaimer in LICENSE |
| Constitution of Maine (Revisor of Statutes, 2023 arrangement) | <https://legislature.maine.gov/doc/10674> | 2026-10-30 | same |

Every word of law in this repository comes from these sources. Lexifina reads them and records each act's dated versions, and the laws that made each change, in one corpus file. This repository is built from that file.

## What is in it

| Act | Title | Versions | Span |
| --- | --- | ---: | --- |
| `constitution` | Constitution of the State of Maine (2023 arrangement) | 1 | 2024-01-16 to 2024-01-16 |
| `criminal-code` | Maine Revised Statutes, Title 17-A. Maine Criminal Code | 1 | 2026-10-01 to 2026-10-01 |
| `property` | Maine Revised Statutes, Title 33. Property | 1 | 2026-10-01 to 2026-10-01 |
| `business-corporation-act` | Maine Revised Statutes, Title 13-C. Maine Business Corporation Act | 1 | 2026-10-01 to 2026-10-01 |

The build made 4 commits:

| Commits | Kind |
| ---: | --- |
| 4 | first version of an act |
| 0 | one law on its in-force day |
| 0 | changes no amendment note explains, credited to the publisher |

Other counts:
- 0 commits on the branch `future`: laws not yet in force on 2026-10-30.
- 0 commits dated 1 January 1970: in force before 1970, with the real day in their `In-force` trailer.
- 0 laws in the record.
- 4 tags.

## Dates

Each commit is dated at noon (America/New_York) on the day the change took effect. The other dates, enacted and published, are trailers.

When a law gives no date of its own, the default rule applies: 1 M.R.S. section 302 and Const. Art. IV, Pt. 3, sec. 16: an act takes effect 90 days after the Legislature adjourns, unless passed as emergency legislation or provided otherwise. https://legislature.maine.gov/statutes/1/title1sec302.html

## How the history is built

`tools/build.py` turns the corpus into this history in one pass: one commit per law, on the day it took effect. The same corpus always gives the same commit hashes. `tools/check_repo.py` reads every version back from git and compares it with the corpus. `tools/on.py` shows the law as it stood on any date. The corpus format is described in `tools/SCHEMA.md`.

- Corpus: sha256 `032b55e1e9be84f24226e29890a76b6c3c8fd13fe6ba99a0fc68b5b7663c9251` (2201164 bytes).
- Builder blob hashes (`git hash-object`): `build.py` `a4faa25af85facb64b956b372f6b528aafdd7ec1`, `check.py` `3e59cb6f05eccb94a9ec14431a7f6781221e83ef`, `on.py` `644a6c0857fbcc72562032b58d57aa113fee0641`.
- Python 3.12.10; git version 2.46.0.windows.1.

## Checks

Not yet run for this build.

No second build of this corpus has been compared yet.

## Decisions made by hand

- The statutes are the Revisor of Statutes section pages: the heading and every text block of each current section, in order. The bracketed session-law history notes after each subsection are not copied. Repealed, reallocated, renumbered and expired sections are left out.
- The statutes are one "oldest version available" version per title, dated 2026-10-01, the date the Revisor states the text is current through (the Second Regular Session of the 132nd Maine Legislature).
- The Constitution is the Revisor's PDF of the 2023 arrangement (Resolve 2023, chapter 86; includes CR 2023, c. 1 and c. 2). It carries no in-force date, so its version is dated 2024-01-16, the PDF's creation date. A section's heading and its first paragraph share one line, as printed; running heads, page numbers, SECTION HISTORY notes and article/part titles are left out.
- The Revisor states that the State of Maine claims a copyright in its codified statutes and requires republications to carry its disclaimer. The disclaimer is reproduced verbatim in LICENSE and README.md.

## What AI did and did not do

The scripts that read the sources and build this repository were written by Claude Code running Claude Opus 5.5 (`claude-opus-5-5`) under Lexifina's direction.

No model wrote, translated or corrected legal text. No model runs at build time. Every word of law in this repository comes from the official sources above.

The commit messages are written by `build.py` from the source data.

Model use at data-build time:
- Claude Code wrote the fetch and parse scripts; it wrote or changed no legal text. The scripts are deterministic and run no model.
