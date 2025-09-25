# Changes

<!-- towncrier release notes start -->

## 1.0.0a2 (2025-09-25)


### Feature

- Add new columns (status, src_level, dst_level) to the path report. @ericof 
- Refactor report generation during pipeline run and allow users to register their own reports to be run. @ericof 
- Support steps to be run before the pipeline to prepare settings and state. @ericof 


### Bugfix

- Fix collective.transmute.pipeline.pipeline._add_to_drop logic. @ericof [#26](https://github.com/collective/collective.transmute/issues/26)
- Handle paths with encoded spaces in `collective.transmute.steps.ids.process_ids`. @ericof [#29](https://github.com/collective/collective.transmute/issues/29)
- Fix issue with transmute not dropping items because of a bug in _add_to_drop. @ericof [#31](https://github.com/collective/collective.transmute/issues/31)
- Fix 'collective.transmute.steps.portal_type.process_type' handling of path.portal_type mapping. @ericof 
- Handle content id ending in _ @ericof 
- Support rewriting path prefixes for content items. @ericof 

## 1.0.0a1 (2025-09-16)


### Feature

- Generate a redirects.json file. @ericof, @jnptk [#23](https://github.com/collective/collective.transmute/issues/23)
- Initial implementation of collective.transmute [@ericof] 
- Use collective.html2blocks version 1.0.0a2. @ericof 


### Bugfix

- Fix Topics ordering not being migrated. @ericof [#9](https://github.com/collective/collective.transmute/issues/9)


### Internal

- Implement GHA workflows. @ericof 


### Documentation

- Deploy package documentation to https://collective.github.io/collective.transmute @ericof
