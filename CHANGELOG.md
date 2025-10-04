# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

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
