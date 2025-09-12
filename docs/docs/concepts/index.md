---
myst:
  html_meta:
    "description": "Comprehensive overview of migration strategies and ETL tools for Plone, including collective.transmute, collective.exportimport, and Transmogrifier."
    "property=og:description": "Comprehensive overview of migration strategies and ETL tools for Plone, including collective.transmute, collective.exportimport, and Transmogrifier."
    "property=og:title": "Plone Migration Concepts and collective.transmute"
    "keywords": "Plone, migration, ETL, collective.transmute, collective.exportimport, Transmogrifier, plone.exportimport, upgrades, glossary"
---

# Migrating Data into {term}`Plone`

Migrating data into {term}`Plone` is a common requirement, whether you are upgrading an older site or moving content from a legacy {term}`CMS`. There are several strategies and tools available, each suited to different scenarios and levels of complexity.

```{note}
For further reading, see:
* [Migration best practices](https://2022.training.plone.org/migrations/index.html)
* [Transmogrifier training](https://2022.training.plone.org/transmogrifier/index.html)
```

## In-Place Migrations (Upgrades)

{term}`Plone` provides built-in upgrade mechanisms to migrate older sites to newer versions using "in-place" upgrades. This approach is often the simplest and fastest when your site has minimal customizations, add-ons, or content types.

For example, upgrading from {term}`Plone` 5.2 (Python 3) to {term}`Plone` 6 Classic is typically straightforward. However, in-place migrations can become complex when dealing with major changes, such as moving from {term}`Plone` 4.3 to {term}`Plone` 6.1, migrating from {term}`Archetypes` to {term}`Dexterity`, or implementing {term}`Volto` support.

## ETL Add-ons for {term}`Plone`

The {term}`Plone` community has developed robust tools for handling migrations using the {term}`ETL` ({term}`Extract`, {term}`Transform`, {term}`Load`) process. Two notable solutions are:

### {term}`Transmogrifier`

Inspired by Calvin's invention in Calvin and Hobbes, {term}`collective.transmogrifier` enables building configurable pipelines to transform content. It supports all three ETL phases and allows you to extract, transform, and load data independently or in combination.

Its modularity and extensibility make it powerful, but its configuration complexity can present a steep learning curve.

### {term}`collective.exportimport`

Created by Philip Bauer, {term}`collective.exportimport` leverages years of migration experience. It can be installed on {term}`Plone` sites (version 4 and above) to export data to {term}`JSON`, applying some transformations during export. The exported data can then be imported into a target {term}`Plone` site using the same add-on.

Developers can extend its functionality by subclassing base classes for custom extraction, transformation, or loading logic.

## Plone Core: {term}`plone.exportimport`

Since {term}`Plone` 6.0 (and as a core package from 6.1), {term}`plone.exportimport` provides standardized export and import capabilities. Inspired by {term}`collective.exportimport`, it offers a predictable directory structure and a clear contract for importing data into {term}`Plone`.

This makes it easier for developers and integrators to move data between recent {term}`Plone` sites.
