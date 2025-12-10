# Changes

<!-- towncrier release notes start -->

## 1.0.0a7 (2025-12-10)


### Feature

- Convert `plone.app.querystring.operation.string.path` to `plone.app.querystring.operation.string.absolutePath` if value points to the root of the portal. @ericof 
- Deduplicate Subject values in a querystring. @ericof 


### Bugfix

- Fix KeyError on cleanup_querystring_item when an operation does not require a value. @ericof [#48](https://github.com/collective/collective.transmute/issues/48)

## 1.0.0a6 (2025-12-10)


### Feature

- Support setting additional fields to be processed by the process_blobs step. @ericof [#42](https://github.com/collective/collective.transmute/issues/42)
- Report command adds now the . @ericof [#45](https://github.com/collective/collective.transmute/issues/45)
- Added support to install Viztracer as a dependency. @ericof 


### Bugfix

- Fix report command to save the generated file under the reports folder defined in the transmute settings. @ericof [#45](https://github.com/collective/collective.transmute/issues/45)

## 1.0.0a5 (2025-10-10)


### Feature

- Added to settings.config the keys prepare_data_location and reports_location. @ericof 
- Implement a 'drop by path' report. @ericof 


### Internal

- Added attributes to PloneItem typed dict. @ericof 

## 1.0.0a4 (2025-10-07)


### Feature

- Add workflow name to the PipelineItemReport. @ericof [#36](https://github.com/collective/collective.transmute/issues/36)
- Implement a step to filter pipeline items by date. @ericof 
- Rewrite one_state_workflow history to simple_publication_workflow. @ericof 

## 1.0.0a3 (2025-10-04)


### Feature

- Upgrade collective.html2blocks to version 1.0.0a3. @ericof 


### Bugfix

- Corretly set the b_size for a Listing block from a Collection. @ericof 
- Filtering of "default_page", "ordering", "local_roles" should be done by inspecting state.seen, not state.uids. @ericof 


### Internal

- Update vscode settings. @ericof 

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
