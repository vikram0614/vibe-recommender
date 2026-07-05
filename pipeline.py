# pipeline.py
import json
from lastfm_similar import build_candidate_pool  # or however you expose it
from yt-candidate-download import download_clip
from clap-embeddings import embed_audio
import os

with open("candidate_pool.json") as f:
    candidate_pool = json.load(f)

embeddings = {}
if os.path.exists("embeddings.json"):
    with open("embeddings.json") as f:
        embeddings = json.load(f)

for key in candidate_pool:
    if key in embeddings:
        continue  # already done, skip — this is your resumability
    artist, track = key.split("|||")
    filepath = download_clip(artist, track, key.replace("|||", "_").replace(" ", "_"))
    if filepath is None:
        continue
    embed = embed_audio(filepath)
    embeddings[key] = embed.tolist()
    os.remove(filepath)

    if len(embeddings) % 20 == 0:
        with open("embeddings.json", "w") as f:
            json.dump(embeddings, f)
        print(f"Progress: {len(embeddings)}/{len(candidate_pool)}")

with open("embeddings.json", "w") as f:
    json.dump(embeddings, f)