import csv
import os
import re
import time
from urllib.parse import quote, unquote

import requests

DEVTO_API_KEY = os.getenv("DEVTO_API_KEY")
HEADERS = {"api-key": DEVTO_API_KEY} if DEVTO_API_KEY else {}

def fetch_followers():
    followers = []
    page = 1
    while True:
        url = f"https://dev.to/api/followers/users?page={page}"
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        followers.extend(data)
        print(f"📦 Page {page}: +{len(data)} followers")
        page += 1
        time.sleep(1)
    print(f"✅ Total followers fetched: {len(followers)}")
    return followers

def fetch_user_profile(username):
    """Return the profile dict, or None if the request failed.

    None (not {}) so a failed fetch can't be mistaken for an empty profile.
    """
    url = f"https://dev.to/api/users/by_username?url={quote(username)}"
    r = requests.get(url, headers=HEADERS)
    if r.status_code == 200:
        return r.json()
    return None

# Fields the old code read with invented defaults. DEV's /users/by_username
# does not return these (checked 2026-11-15), so they must be recorded as
# missing, never filled in. See data/devto_bot_audit_full.NOTE.md.
COUNT_FIELDS = ("public_articles_count", "followers_count", "followed_users_count")

def _blank(value):
    """CSV cell for a value that may be missing: '' means 'not returned by the API'."""
    return "" if value is None else value

def is_default_avatar(url):
    """True/False when there is an image URL, None when there is none.

    DEV now serves avatars through an image proxy that embeds the original
    URL percent-encoded, so endswith() never matched; decode and search.
    """
    if not url:
        return None
    return "default_profile_image" in unquote(url)

def score_account(username):
    if not username:
        return {"Username": None, "HeuristicScore": 0, "HeuristicReasons": "no username"}

    profile = fetch_user_profile(username)
    if profile is None:
        return {"Username": username, "HeuristicScore": "", "HeuristicReasons": "",
                "MissingFields": "profile fetch failed"}

    score = 0
    notes = []
    missing = [f for f in COUNT_FIELDS if profile.get(f) is None]
    if not profile.get("profile_image"):
        missing.append("profile_image")

    # NOTE: hash-style usernames are common among ordinary new DEV accounts
    # (~37-50% of non-follower baseline samples, 2026-11-15). Weak signal.
    if re.match(r"^[_\-0-9a-f]{6,}$", username):
        score += 1
        notes.append("Suspicious username")
    if not (profile.get("summary") or "").strip():
        score += 1
        notes.append("Empty bio")

    posts = profile.get("public_articles_count")
    if posts == 0:
        score += 1
        notes.append("No posts")

    avatar_default = is_default_avatar(profile.get("profile_image"))
    if avatar_default:
        score += 1
        notes.append("Default profile image")

    followers = profile.get("followers_count")
    following = profile.get("followed_users_count")
    if followers is not None and following is not None:
        if following > 10 and followers / following < 0.1:
            score += 1
            notes.append("Low follower/following ratio")

    joined = profile.get("joined_at") or ""

    return {
        "Username": username,
        "Bio": profile.get("summary") or "",
        "PostCount": _blank(posts),
        "AvatarDefault": _blank(avatar_default),
        "AvatarURL": profile.get("profile_image") or "",
        "JoinedDate": joined,
        "Followers": _blank(followers),
        "Following": _blank(following),
        "HeuristicScore": score,
        "HeuristicReasons": "; ".join(notes),
        "MissingFields": ";".join(missing),
        "AIScore": "",
        "AIJustification": ""
    }

def run_audit():
    followers = fetch_followers()
    if not followers:
        print("⚠️ No followers retrieved. Check your API key.")
        return

    results = []
    for i, f in enumerate(followers, 1):
        username = f.get("username")
        print(f"[{i}/{len(followers)}] Fetching {username}")
        row = score_account(username)
        results.append(row)
        time.sleep(0.5)

    if not results:
        print("⚠️ No data. Exiting.")
        return

    fieldnames = ["Username", "Bio", "PostCount", "AvatarDefault", "AvatarURL",
                  "JoinedDate", "Followers", "Following", "HeuristicScore",
                  "HeuristicReasons", "MissingFields", "AIScore", "AIJustification"]
    with open("devto_bot_audit_full.csv", "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, restval="")
        writer.writeheader()
        writer.writerows(results)

    print("✅ DONE. Output saved to devto_bot_audit_full.csv")
    print(f"✅ Account rows written: {len(results)}")

if __name__ == '__main__':
    run_audit()
