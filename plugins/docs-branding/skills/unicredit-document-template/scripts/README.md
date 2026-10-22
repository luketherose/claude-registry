# Scripts

Both scripts read `../assets/doc-tokens.json` and need `python3` with `python-docx`.

## build_uc_docx.py

Renders a JSON spec into a DOCX that follows the template.

```bash
python3 scripts/build_uc_docx.py <spec.json> <out.docx> [--logo <image> | --logo-from <docx>]
```

- `spec.json`: the content, in the format of `references/spec-format.md`.
- `out.docx`: written, overwritten when it exists.
- `--logo`: a PNG or JPG of the UniCredit logo.
- `--logo-from`: an existing UniCredit `.docx`; the first image under `word/media/` is used,
  and its name is printed on stderr so the choice can be verified.
- Without either, the cover carries a grey `[UniCredit logo]` placeholder and a warning is
  printed; the checker then warns too.

Exit codes: `0` written, `1` invalid spec (the reason follows `invalid spec:` on stderr),
`2` usage or I/O error, including a missing logo file or an unreadable source document.

## check_uc_docx.py

Checks any DOCX against the template and prints what a reader would see.

```bash
python3 scripts/check_uc_docx.py <file.docx>
```

Output, in this order:

1. Page size and margins in cm.
2. The outline: every Heading 1 and Heading 2, indented.
3. The Part labels found.
4. One line per table: row count and header cells.
5. The count of `[TBC]` and `[Proposed]` tags.
6. One `ERROR` or `WARN` line per finding, then the totals.

`ERROR` covers: margins, fonts other than Arial in the body, in the styles it uses or in the
document defaults (theme fonts included), colours, fills or borders outside the palette, em
dashes, a missing TOC field, broken section numbering, a Heading 2 without its parent
number, missing Part labels, annexes without the `ANNEXES` label, a missing Document control
page, a section 1 without Purpose, Scope and Related documents, a table header that does not
repeat or is not filled, any of the seven mandatory tables missing, a first table that is
not the cover metadata, and `[TBC]` tags with no open points table.

`WARN` covers: a page size other than the template's, font sizes outside the scale, a double
hyphen, a cover that does not open on an image, no update-fields-on-open setting, an Open
points section that is not the last numbered one, and a Glossary that is not the last annex.

Exit codes: `0` no `ERROR`, `1` at least one `ERROR`, `2` unreadable file.
