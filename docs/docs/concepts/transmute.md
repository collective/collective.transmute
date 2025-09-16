---
myst:
  html_meta:
    "description": "Comprehensive overview of migration strategies and ETL tools for Plone, including collective.transmute, collective.exportimport, and Transmogrifier."
    "property=og:description": "Comprehensive overview of migration strategies and ETL tools for Plone, including collective.transmute, collective.exportimport, and Transmogrifier."
    "property=og:title": "Plone migration concepts and collective.transmute"
    "keywords": "Plone, migration, ETL, collective.transmute, collective.exportimport, Transmogrifier, plone.exportimport, upgrades, glossary"
---


# Why `collective.transmute`?

With several migration options available, why introduce another tool?

{term}`collective.transmute` is designed to focus exclusively on the "transform" step of the {term}`ETL` process:

Extract
:   Use {term}`collective.exportimport` on the source site to export data, optionally applying initial transformations.
    For example, transform {term}`Archetypes` to {term}`Dexterity`, or Topics to Collections.

Transform
:   Apply repeatable, testable, and extensible transformations to the exported data using {term}`collective.transmute`.
    This step is independent of both the source and target environments.

Load
:   Import the transformed data into {term}`Plone` using {term}`plone.exportimport`, without needing extra add-ons in production.

This separation allows developers to focus on transformation logic, debug migration issues efficiently, and avoid unnecessary re-exporting or re-importing of data.

## Design goals

No dependency on {term}`Plone` or {term}`Zope` packages
:   Transformations can be run quickly and independently, without installing additional software.

Repeatable and testable transformation process
:   Generates reports comparing source and transformed data, supporting transparency and troubleshooting.

Extensible by third-party developers
:   Lessons learned from {term}`Transmogrifier` are applied, enabling integrators to implement custom business logic and transformation steps.

{term}`collective.transmute` empowers you to build focused, maintainable, and efficient migration workflows for {term}`Plone`, making the transformation phase modular, testable, and developer-friendly.
