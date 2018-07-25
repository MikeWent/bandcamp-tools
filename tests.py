import pprint
import random
import bc

ALBUM_URL = "https://shirobon.bandcamp.com/album/reject"
TRACK_URL = "https://shirobon.bandcamp.com/track/cloud-chaser"
RANDOM_TAG = random.choice(bc.get_all_tags()["tags"])


def stdout(*smth):
    for x in smth:
        pprint.pprint(x, indent=4)


print(":: Album info")
album_info = bc.get_album(ALBUM_URL)
stdout(album_info)
assert isinstance(album_info, bc.Album)
assert album_info.url == ALBUM_URL

print("\n:: Track info")
track_info = bc.get_track(TRACK_URL)
stdout(track_info)
assert isinstance(track_info, bc.Track)

print("\n:: First 3 tracks in album")
first_three_tracks = bc.get_album_tracklist(ALBUM_URL)[:3]
stdout(first_three_tracks)
assert len(first_three_tracks) == 3
assert [isinstance(x, bc.Track) for x in first_three_tracks]

print(f"\n:: Random album by tag '{RANDOM_TAG}'")
random_album_by_tag = random.choice(bc.search_albums_by_tag(RANDOM_TAG))
assert isinstance(random_album_by_tag, bc.Album)
stdout(random_album_by_tag)

print(f"\n:: First album by tag '{RANDOM_TAG}' (generator=True)")
first_album_by_tag_generator = next(bc.search_albums_by_tag(RANDOM_TAG, generator=True))
assert isinstance(first_album_by_tag_generator, bc.Album)
stdout(first_album_by_tag_generator)
