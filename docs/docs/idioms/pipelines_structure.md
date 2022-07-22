# Pipelines structure

## Pipelines begining

A pipeline should always begins with a **generating command**.
Although the pipelines runners allows to start with a **streaming command**,
this is to be considered as a syntatic sugar.

The `echo` command yields either the previous event or an empty one:

```
| echo
```

## Monitoring and tracing

The `mpl-report` command (aliases: `report`, `mpl_report`) provide a pipeline
reporting mechanism to trace the pipeline status.

`mpl-report` takes a pipeline as first argument. This pipeline may be used
to print the report, to formar and send it on logging server, etc.

If the command is given a _frequency_ as second argument, the reporting
pipeline will run every _frequency_ event.

This meta command runs by default right before the pipeline execution, and
right after its ending.

`mpl-report` can be invoked anywhere in the pipeline, and of course multiple
time.

```
| make showinfo=yes
| report [ | echo | output format='raw' ]
| output format='hjson'
```

```
{'pipeline': {'name': 'main', 'state': 'running', 'errors': {'count': 0, 'list': {}}}, 'report': {'frequency': -1}}

{
  "id": 0,
  "chunk": {
    "chunk": 0,
    "chunks": 1
  },
  "count": {
    "begin": 0,
    "end": 1
  },
  "pipeline": {
    "name": "main"
  }
}

{'pipeline': {'name': 'main', 'state': 'ending', 'errors': {'count': 0, 'list': {}}}, 'report': {'frequency': -1}}
```

---
