# M42PL - A Data Manipulation Language

M42PL is a _Data Manipulation Language_, inspired by
[Unix shells][unixshells] and [Splunk][splunk].

The language is extremely simple to learn and to use, yet powerfull and versatile.
It is designed to make data manipulation trivial, even for non-technical users.

## Examples

**Query an URL**

```
| url 'https://api.ipify.org'
| fields response.content, response.status
| eval message = 'Your external IP is ' + response.content
```

**Run a HTTP server**

```
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
    '*' on '/{path}' = []
```

**Capture and stream a video**

> This requires the installation of [m42pl-vision][m42pl-vision]

```
| cv2_read
| cv2_resize ratio=0.5
| zmq_pub topic='webcam'
```

**Display a video stream**

> This requires the installation of [m42pl-vision][m42pl-vision]

```
| zmq_sub topic='webcam'
| decode {zmq.frames[0]} with 'msgpack'
| cv2_show cv2.frame
```


---

[unixshells]: https://en.wikipedia.org/wiki/Shell_script
[splunk]: https://splunk.com
[m42pl-commands]: https://github.com/jpclipffel/m42pl-commands
[m42pl-dispatchers]: https://github.com/jpclipffel/m42pl-dispatchers
[m42pl-vision]: https://github.com/jpclipffel/m42pl-vision