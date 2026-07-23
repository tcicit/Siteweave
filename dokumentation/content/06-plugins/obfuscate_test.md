---
author: TCI
breadcrumbs: true
date: '2026-03-08'
draft: false
featured_image: ''
layout: doc
pdf_exclude: true
release_date: '2026-03-08'
tags:
- Plugin
- Documentation
title: Plugin — Obfuscate
weight: 130
---

The `obfuscate` plugin protects sensitive text — email addresses, phone numbers, and physical addresses — from spam bots by replacing characters with HTML entities. The text remains readable to humans in the browser.

## Syntax

```markdown
[[obfuscate]]contact@example.com[[/obfuscate]]

[[obfuscate]]+41 44 123 45 67[[/obfuscate]]
```

## How It Works

The plugin converts each character of the enclosed text into its HTML entity equivalent:

- `c` → `&#99;`
- `o` → `&#111;`
- `@` → `&#64;`
- `.` → `&#46;`

The browser renders these entities as normal text, but automated web scrapers see only character codes — making it far harder to harvest contact details.

## Automatic Obfuscation

You don't always need the plugin manually. The **renderer automatically obfuscates** the following from your `config.yaml`:

```yaml
contact:
  email: john@example.com    ← automatically obfuscated in all HTML output
  phone: +1 234 567 8900     ← automatically obfuscated
  address: 12345 Sampletown  ← automatically obfuscated
```

Use the `[[obfuscate]]` plugin for any additional sensitive text that appears directly in your Markdown content.

## Examples

**Email address:**

```markdown
Contact us at: [[obfuscate]]hello@mysite.com[[/obfuscate]]
```

**Phone number:**

```markdown
Call us: [[obfuscate]]+41 44 123 45 67[[/obfuscate]]
```

**Full contact block:**

```markdown
| Field | Value |
| :--- | :--- |
| Email | [[obfuscate]]sales@example.com[[/obfuscate]] |
| Phone | [[obfuscate]]+1 800 555 0100[[/obfuscate]] |
| Office | [[obfuscate]]1 Infinite Loop, Cupertino, CA[[/obfuscate]] |
```

[[infobox type="info" title="Privacy Best Practice"]]
For production websites, store all contact details in `config.yaml` under the `contact` key. The renderer obfuscates them automatically in every page's HTML output — no manual plugin calls required.
[[/infobox]]
