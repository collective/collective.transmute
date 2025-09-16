---
myst:
  html_meta:
    "description": "Comprehensive overview of migration strategies and ETL tools for Plone, including collective.transmute, collective.exportimport, and Transmogrifier."
    "property=og:description": "Comprehensive overview of migration strategies and ETL tools for Plone, including collective.transmute, collective.exportimport, and Transmogrifier."
    "property=og:title": "Plone Migration Concepts and collective.transmute"
    "keywords": "Plone, migration, ETL, collective.transmute, collective.exportimport, Transmogrifier, plone.exportimport, upgrades, glossary"
---

# Migrate data into Plone

Migrating data into {term}`Plone` is a common requirement, whether you are upgrading an older site or moving content from a legacy {term}`CMS`.
There are several strategies and tools available, each suited to different scenarios and levels of complexity.

```{seealso}
Further reading:

-   {doc}`training-2022:migrations/index`
-   {doc}`training-2022:transmogrifier/index`
```

## In-place migrations (upgrades)

Plone provides built-in upgrade mechanisms to migrate older sites to newer versions using in-place upgrades.
This approach is often the simplest and fastest when your site has minimal customizations, add-ons, or content types.

For example, upgrading from Plone 5.2 (Python 3) to Plone 6 Classic is typically straightforward.
However, in-place migrations can become complex when dealing with major changes, such as moving from Plone 4.3 to Plone 6.1, migrating from {term}`Archetypes` to {term}`Dexterity`, or implementing {term}`Volto` support.

## ETL add-ons and packages for Plone

The Plone community has developed robust tools for handling migrations using the extract, transform, and load (ETL) process.
Notable solutions include, in the order of their creation, Transmogrifier, `collective.exportimport`, and `plone.exportimport`.

### Transmogrifier

Inspired by Calvin's invention in Calvin and Hobbes, {term}`collective.transmogrifier` enables building configurable pipelines to transform content.
It supports all three ETL phases and allows you to extract, transform, and load data independently or in combination.

Its modularity and extensibility make it powerful, but its configuration complexity can present a steep learning curve.

### `collective.exportimport`

Created by Philip Bauer, {term}`collective.exportimport` leverages years of migration experience.
It can be installed on Plone sites (version 4 and above) to export data to {term}`JSON`, applying some transformations during export.
The exported data can then be imported into a target Plone site using the same add-on.

Developers can extend its functionality by subclassing base classes for custom extraction, transformation, or loading logic.

### `plone.exportimport`

{term}`plone.exportimport` is a slimmer version of `collective.exportimport`.
While `collective.exportimport` supports older Plone versions and Python 2, and also takes care of data conversion from Archetypes to Dexterity, `plone.exportimport` focuses only on latest Plone and Python.
It offers a predictable directory structure and a clear contract for importing data into Plone.
This makes it easier for developers and integrators to move data between recent Plone sites.

In Plone 6.0.x versions, `plone.exportimport` was a separate add-on.
It became a Plone core package in 6.1.0.
