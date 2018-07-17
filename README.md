# bandcamp-tools

Installation: `pip3 install --user --upgrade -r requirements.txt`

## Radio

Generate a playlist from Bandcamp search results.

### Example

```bash
bc_radio.py --tag depressive-black-metal -o random_music.pls
```

Available tags: [here](https://bandcamp.com/tags).

### More details

```
usage: bc_radio.py [-h] (-l | -t TAG) [-o FILE] [-p | -m] [-n N]

optional arguments:
  -h, --help            show this help message and exit
  -l, --list-tags       show all available music tags
  -t TAG, --tag TAG     music tag to search
  -o FILE, --output FILE
                        output playlist filename
  -p, --pls             generate .pls file (default)
  -m, --m3u8            generate .m3u8 file
  -n N, --number N      minimal number of albums to fetch, default is 30
```

## Download albums/tracks

_Coming soon..._

