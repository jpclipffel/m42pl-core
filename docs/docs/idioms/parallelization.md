# Parallelization

M42PL provides two mechanisms to parallelize the pipelines:

* _Implicit_: Parallelization is handled by the selected _dispatcher_,
  which control the pipelines structure to make them run on multiples
  CPU, nodes, etc.
* _Explicit_: On the top of the dispatcher, some commands allow to
  _split_ and _merge_ the pipelines.


## Split a pipeline

A pipeline can be split in multiples sub-pipelines using the 
`parallel` (or `tee`) command.

```
| make count=10 showinfo=yes
| parallel
  [ | echo | eval p=1 | stats count by p ],
  [ | echo | eval p=2 | stats max(id) by p ]
```

Output:

```json
{
  "p": 1,
  "count()": 10
}

{
  "p": 2,
  "max(id)": 9
}

```

---
