#!/usr/bin/env python3

from random import choice as choice_random
import argparse

args = argparse.ArgumentParser()
args_tag = args.add_mutually_exclusive_group(required=True)
args_tag.add_argument("-l", "--list-tags", help="show all available music tags", action="store_true")
args_tag.add_argument("-t", "--tag", help="music tag to search", default=None)
args.add_argument("-o", "--output", help="output playlist filename", metavar="FILE")
args_format = args.add_mutually_exclusive_group()
args_format.add_argument("-p", "--pls", help="generate .pls file (default)", action="store_true", default=True)
args_format.add_argument("-m", "--m3u8", help="generate .m3u8 file", action="store_true")
args.add_argument("-n", "--number", help="minimal number of albums to fetch, default is 30", default=30, type=int, metavar="N")
options = args.parse_args()

if not options.output and not options.list_tags:
    print("Error: -o/--output isn't specified.")
    print("See -h/--help for details.")
    exit(1)

# Import heavy bc module after parsing command line to save time
import bc

PLS_HEADER = "[playlist]"
PLS_ENTRY = """
File{n}={url}
Title{n}={artist} - {title}
Length{n}={duration}"""
PLS_FOOTER = """
NumberOfEntries={n}
Version=2"""

M3U8_HEADER = "#EXTM3U"
M3U8_ENTRY = "#EXTINF:{duration},{artist} - {title}\n{url}"


def generate_pls(tracklist):
    result = PLS_HEADER
    for n, track in enumerate(tracklist, start=1):
        result += PLS_ENTRY.format(
            url=track.url,
            artist=track.artist,
            title=track.title,
            duration=float(track.duration),
            n=n)
    result += PLS_FOOTER.format(n=len(tracklist))
    return result


def generate_m3u8(tracklist):
    result = M3U8_HEADER
    for track in tracklist:
        result += M3U8_ENTRY.format(
            duration=float(track.duration),
            artist=track.artist,
            title=track.title,
            url=track.url)
    return result

if options.list_tags:
    print(", ".join([tag for tag in bc.get_all_tags()]))
    exit()

if not options.tag:
    tag = choice_random(bc.get_all_tags())
    print(f":: Randomly choosen tag: {tag}")
else:
    tag = options.tag

print(":: Fetching", options.number, "albums...")
albums_n = 0
tracklist = []
for album in bc.search_albums_by_tag(tag, generator=True):
    if albums_n >= options.number:
        break
    albums_n += 1
    print(" ", albums_n, ". ", album.url, sep="")
    tracks = bc.get_album_tracklist(album)
    for track in tracks:
        tracklist.append(track)

print(":: Total", len(tracklist), "tracks")
if options.m3u8:
    print(":: Generating .m3u8 playlist")
    playlist = generate_m3u8(tracklist)
elif options.pls:
    print(":: Generating .pls playlist")
    playlist = generate_pls(tracklist)
with open(options.output, "w") as f:
    f.write(playlist)
    print(":: Saved to file ", options.output, sep="")
