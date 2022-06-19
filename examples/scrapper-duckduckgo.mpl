| make
| eval
    url = 'https://html.duckduckgo.com/lite',
    form.q = 'hello, world',
| foreach [
    | until `response.status != 200` [
        | url url method='POST' data=form headers=headers
        | xpath '//a[@class="result-link"]' src=response.content dest=links
        | eval
            form.s = field(form.s, -20) + 50,
            form.o = 'json',
            form.dc = field(form.dc, 0) + len(links) + 1,
            form.api = '/d.js',
            form.kl = 'wt-wt',
        | fields - response.content
        | sleep 1
    ]
]
| fields links
| expand links
| output buffer=1
