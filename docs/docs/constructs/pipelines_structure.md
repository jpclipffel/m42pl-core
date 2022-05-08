# Pipelines structure

## Pipelines begining

A pipeline should always begins with a **generating command**.
Although the pipelines runners allows to start with a **streaming command**,
this is to be considered as a syntatic sugar.

The `echo` command yields either the previous event or an empty one:

```
| echo
```

---
