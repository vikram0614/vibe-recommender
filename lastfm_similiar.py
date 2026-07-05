import os
import json
import requests
import time

LASTFM_API_KEY = os.environ["LASTFM_API_KEY"]

def get_similar_tracks(artist, track, limit=200):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.getsimilar", "artist": artist, "track": track,
        "api_key": LASTFM_API_KEY, "format": "json", "limit": limit,
        "autocorrect": 1
    }
    resp = requests.get(url, params=params).json()
    if "error" in resp:
        print(f"Error for {artist} - {track}: {resp.get('message')}")
        return []
    return resp.get("similartracks", {}).get("track", [])

def get_similar_tracks_with_fallback(artist, track, min_threshold=20):
    similar = get_similar_tracks(artist, track)
    if len(similar) >= min_threshold:
        return similar

    print(f"Thin data for {artist} - {track} ({len(similar)} results), falling back to artist-level")
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.getsimilar", "artist": artist,
        "api_key": LASTFM_API_KEY, "format": "json", "limit": 15,
        "autocorrect": 1
    }
    resp = requests.get(url, params=params).json()
    similar_artists = resp.get("similarartists", {}).get("artist", [])

    fallback_candidates = []
    for a in similar_artists:
        top_tracks_params = {
            "method": "artist.gettoptracks", "artist": a["name"],
            "api_key": LASTFM_API_KEY, "format": "json", "limit": 10
        }
        tt_resp = requests.get(url, params=top_tracks_params).json()
        tracks = tt_resp.get("toptracks", {}).get("track", [])
        for t in tracks:
            fallback_candidates.append({
                "artist": {"name": t["artist"]["name"]},
                "name": t["name"]
            })
        time.sleep(0.2)

    return fallback_candidates

SEED_SONGS = [
    ("A$AP Rocky", "LVL"),
    ("Lil B", "Back Home"),
    ("Drake", "Marvins Room"),
    ("$uicideboy$", "Runnin' Thru the 7th with My Woadies"),
    ("Nujabes", "Luv(sic)"),
    ("Hikaru Utada", "One Last Kiss"),
    ("Beach House", "Lemon Glow"),
    ("Smokedope2016", "IM NOT GOD BUT I WISH I WAS(feat. Joeyy)"),
    ("Oliver Francis", "AEOU"),
    ("BETWEEN FRIENDS", "Affection"),
    ("MIRRAR", "Love Letters to Maryjane"),
    ("Kodak Black", "Skrt"),
    ("Lucki", "Alternative Trouble"),
    ("Tory Lanez", "The Color Violet"),
    ("$uicideboy$", "Avalon"),
]

candidate_pool = {}  # (artist, track) -> set of seed songs that surfaced it

def resolve_track(artist, track):
    url = "http://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.search", "track": track, "artist": artist,
        "api_key": LASTFM_API_KEY, "format": "json"
    }
    resp = requests.get(url, params=params).json()
    matches = resp.get("results", {}).get("trackmatches", {}).get("track", [])
    if not matches:
        return None
    top = matches[0]
    return top["artist"], top["name"]

for seed_artist, seed_track in SEED_SONGS:
    resolved = resolve_track(seed_artist, seed_track)
    if resolved is None:
        print(f"Could not resolve seed: {seed_artist} - {seed_track}")
        continue
    real_artist, real_track = resolved
    similar = get_similar_tracks_with_fallback(real_artist, real_track)
    print(f"{real_artist} - {real_track}: {len(similar)} candidates")
    for s in similar:
        key = (s["artist"]["name"], s["name"])
        candidate_pool.setdefault(key, set()).add(f"{real_artist} - {real_track}")
    time.sleep(0.3)
    
with open("candidate_pool.json", "w") as f:
    serializable = {f"{a}|||{t}": list(seeds) for (a, t), seeds in candidate_pool.items()}
    json.dump(serializable, f)

print(f"Total unique candidates: {len(candidate_pool)}")
print(f"Saved candidate_pool.json")