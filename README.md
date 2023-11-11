# Quick Start

## Setting Env Var

### GOOGLE_APPLICATION_CREDENTIALS
* Windows PowerShell -> `$env:GOOGLE_APPLICATION_CREDENTIALS = "{PATH_TO_KEY_JSON}"`
* MacOS / Linux -> `export GOOGLE_APPLICATION_CREDENTIALS={PATH_TO_KEY_JSON}`


## Run Server
```sh=
python server\app.py --driver '{PATH_TO_CHROMEDRIVER}'
```