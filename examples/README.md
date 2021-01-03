# M42PL - Examples

M42PL scripts examples.
Scripts can be run with `m42pl run <script_name>.mpl`.

### Script - `external-ip.mpl`

Query the famous `api.ipify.org`.

### Script - `commands.mpl`

Returns a cleaned list of available M42PL commands.

### Script - `scrapper-music.mpl`

Scrapes Lorne Balfe's Ghost In The Shell MP3 files from the artist web site.

### Script - `scrapper-duckduckgo.mpl`

Searches on DuckDuckGo and returns each result as an event.

### Script - `server-http.mpl`

Basic HTTP server.

Once started, test with with `curl -X POST http://127.0.0.1:8080 -d '{"hello": "world"}'`.
