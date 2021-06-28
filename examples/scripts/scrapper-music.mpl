| url 'http://lornebalfe.com/projects/ghost-in-the-shell/' count=1
| xpath '//noscript//a/@href' src=response.content dest=links.mp3
| fields links
| expand links.mp3
| eval links.filename = basename(links.mp3)
| rename links as link
| output
