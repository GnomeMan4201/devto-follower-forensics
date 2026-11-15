"""Regression tests: missing API fields must stay missing, never become data."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scoring"))
import devto_audit_core_FIXED as core

# What /api/users/by_username actually returned on 2026-11-15 (no count fields).
REAL_SHAPE = {
    "type_of": "user", "id": 3612345, "username": "someone_a1b2c3",
    "name": "Someone", "summary": "", "twitter_username": None,
    "github_username": None, "website_url": None, "location": None,
    "joined_at": "Nov 15, 2025",
    "profile_image": "https://media2.dev.to/dynamic/image/width=640,height=640,"
                     "fit=cover,gravity=auto,format=auto/https%3A%2F%2Fdev-to-uploads"
                     ".s3.amazonaws.com%2Fuploads%2Fuser%2Fprofile_image%2F3612345%2Fabc.png",
}

def _score(monkeypatch, profile, username="someone_a1b2c3"):
    monkeypatch.setattr(core, "fetch_user_profile", lambda u: profile)
    return core.score_account(username)

def test_missing_counts_are_blank_not_defaults(monkeypatch):
    row = _score(monkeypatch, dict(REAL_SHAPE))
    assert row["Following"] == ""        # was 1
    assert row["Followers"] == ""        # was 0
    assert row["PostCount"] == ""        # was 0
    assert "No posts" not in row["HeuristicReasons"]
    for f in core.COUNT_FIELDS:
        assert f in row["MissingFields"]

def test_present_counts_are_used(monkeypatch):
    p = dict(REAL_SHAPE, public_articles_count=0, followers_count=0, followed_users_count=50)
    row = _score(monkeypatch, p)
    assert row["Following"] == 50 and row["PostCount"] == 0
    assert "No posts" in row["HeuristicReasons"]
    assert "Low follower/following ratio" in row["HeuristicReasons"]
    assert row["MissingFields"] == ""

def test_proxied_default_avatar_detected(monkeypatch):
    url = ("https://media2.dev.to/dynamic/image/width=640/https%3A%2F%2Fdev.to%2F"
           "assets%2Fdefault_profile_image.png")
    assert core.is_default_avatar(url) is True
    assert core.is_default_avatar(REAL_SHAPE["profile_image"]) is False
    assert core.is_default_avatar("") is None

def test_failed_fetch_is_flagged_not_scored(monkeypatch):
    row = _score(monkeypatch, None)
    assert row["HeuristicScore"] == ""
    assert row["MissingFields"] == "profile fetch failed"
