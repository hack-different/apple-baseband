# apple-baseband
RE tooling kit for Apple modem baseband

## General Approach

* Accept BBFW file
* Extract Qualcomm FBPT (imjtool for instance)
* Identify trustlets (.msm) and join them into ELF files
* Identify updaters and extract payloads

## Reference

* https://github.com/rpw/hexagon

## Credits

### `unify_trustlet.py`

https://github.com/laginimaineb/unify_trustlet.git