| http_server with
    '*' on '/foo' = [
        | echo
        | eval path='foo', mode='infinite+iterator'
        | fields path, mode
    ],
    '*' on '/bar' = [
        | eval path='bar', mode='infinite+stream'
        | fields path, mode
    ],
    '*' on '/{path}' = [
        | eval path=request.path, mode='default'
        | fields path, mode
    ]
