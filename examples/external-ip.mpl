| curl 'https://api.ipify.org'
| fields response.content, response.status
| eval message = 'Your external IP is ' + response.content
| output
