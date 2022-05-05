<!-- vim: set ft=Markdown ts=4 -->

# Pipeline fields

Pipeline fields returns the result of a sub-pipeline.
They are similar to some programming languages _functions_.

## Syntax

Pipelines fields are literal pipelines:

```
| make count=3
| output format=[ | make | eval format='json' ]
```

!!! note "Pipeline fields output"
    As most commands attributes excepts a single value or a list of values,
    the pipeline fields post-process their result.
    
    If the pipeline yields a single event and if this single event contains a
    single field, then the pipeline field return this single value.

    Otherwise, the latest event is returned whole.
