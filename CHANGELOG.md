# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 1.0.0a5 (2026-05-18)


### Bugfix

- Fixed `<ul>` and `<ol>` elements that contain orphan text without `<li>` children: the content is now wrapped into a synthetic `<li>` so it survives conversion instead of being silently dropped. @ericof [#29](https://github.com/collective/collective.html2blocks/issues/29)

## 1.0.0a4 (2026-05-15)


### Feature

- Also publish container images for arm64. @ericof [#20](https://github.com/collective/collective.html2blocks/issues/20)


### Bugfix

- Better handling of tables. @ericof [#22](https://github.com/collective/collective.html2blocks/issues/22)
- Fixed conversion of paragraphs starting with an inline element wrapping only whitespace (e.g. `<b>&nbsp;</b>`) — the rest of the paragraph text was being silently dropped from the Slate value while `plaintext` stayed correct. @ericof [#25](https://github.com/collective/collective.html2blocks/issues/25)
- Normalized whitespace in the Slate `plaintext` attribute — non-breaking spaces and runs of consecutive whitespace are now collapsed into a single space, so search and preview behave consistently. The Slate `value` (node text) is left untouched. @ericof [#26](https://github.com/collective/collective.html2blocks/issues/26)
- Fixed conversion of images wrapped in an inline element (e.g. `<b>`, `<strong>`) inside a paragraph — the images are now correctly emitted as Volto image blocks instead of being silently dropped along with the surrounding wrapper. @ericof [#27](https://github.com/collective/collective.html2blocks/issues/27)

## 1.0.0a3 (2025-10-04)


### Bugfix

- Ensure correct type for each item handled in collective.html2blocks.utils.slate.process_top_level_items. @ericof [#18](https://github.com/collective/collective.html2blocks/issues/18)


### Internal

- Do not package the build documentation with the source package. @ericof 
- Update vscode settings. @ericof 


### Documentation

- Documentation: Ignore CHANGELOG.md during vale checks. @ericof 

## 1.0.0a2 (2025-09-12)


### Bugfix

- Fix issue with packaging collective.html2blocks as a wheel. @ericof 


### Documentation

- Clean up initial documentation. @stevepiercy [#15](https://github.com/collective/collective.html2blocks/issues/15)
- Deploy documentation to https://collective.github.io/collective.html2blocks. @ericof [#16](https://github.com/collective/collective.html2blocks/issues/16)

## 1.0.0a1 (2025-09-11)


### Feature

- Implemented `collective.html2blocks.converters.volto_blocks` function [@ericof] [#4](https://github.com/collective/collective.html2blocks/issues/4)
- Initial implementation of collective.volto2blocks [@ericof] 
- Wrap block elements -- like img, video, table -- in their own paragraph if nested inside an existing paragraph. @ericof 


### Bugfix

- Handle headers (h1, h2) that contain only an image inside [@ericof] [#5](https://github.com/collective/collective.html2blocks/issues/5)
- Do not generate a slate block for empty lists. @ericof [#6](https://github.com/collective/collective.html2blocks/issues/6)
- Top level items in a Slate block should be wrapped in a paragraph. @ericof [#8](https://github.com/collective/collective.html2blocks/issues/8)
- Better handling of <br> tags. @ericof 
- Fix table rows duplicating the number of cells due to the existence of line breaks or comments @ericof 


### Internal

- Implement GitHub Actions workflows. @ericof 


### Documentation

- Base documentation for collective.html2blocks. @ericof [#1](https://github.com/collective/collective.html2blocks/issues/1)
