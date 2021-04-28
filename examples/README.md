# M42PL - Examples

M42PL scripts examples.
Scripts can be run with `m42pl run <script_name>.mpl`.

## Scripts

### `external-ip.mpl`

Query the famous `api.ipify.org`.

### `commands.mpl`

Returns a cleaned list of available M42PL commands.

### `scrapper-music.mpl`

Scrapes Lorne Balfe's *Ghost In The Shell* tracks URL from the artist web site.

### `server-http.mpl`

HTTP server which listen on `127.0.0.1:8080` by default and accept any requests
(`GET`, `POST`, ...) on the following paths:

* `/foo`
* `/bar`
* `/{path}` (replace `{path}` with a value like `my-path`, e.g. `/my-path`)

You may test it with `curl` or `ab`:

* `curl -Lki http://127.0.0.1:8080/foo`
* `ab -n 100 -c 100 http://127.0.0.1:8080/bar`
