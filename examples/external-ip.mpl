| curl 'https://api.ipify.org' count=1
| fields response.content, response.status
| eval message = 'Your external IP is ' + response.content
| output format=json
