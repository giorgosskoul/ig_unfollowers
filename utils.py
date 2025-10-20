
import argparse, csv, json, sys
from pathlib import Path

def load_followers(data_dir: Path) -> set[str]:
    """
    Supports both formats:
    1) followers_1.json, followers_2.json, ...  -> a JSON array; each item has string_list_data[]
    2) followers.json                            -> {"relationships_followers": [ ... ]}
    And older oddities where string_list_data may appear at the root dict.
    """
    followers = set()

    def add_from_string_list(items):
        for it in items or []:
            v = (it.get("value") or "").strip().lstrip("@").lower()
            if v:
                followers.add(v)

    # case A: multiple part files: followers_*.json
    for f in sorted(data_dir.glob("followers_*.json")):
        try:
            obj = json.loads(f.read_text(encoding="utf-8"))

            if isinstance(obj, list):
                # Your file matches this branch
                for entry in obj:
                    add_from_string_list(entry.get("string_list_data"))
            elif isinstance(obj, dict):
                # Sometimes IG puts string_list_data directly at root
                if "string_list_data" in obj:
                    add_from_string_list(obj.get("string_list_data"))
                # Or wraps under relationships_followers
                for entry in obj.get("relationships_followers", []):
                    add_from_string_list(entry.get("string_list_data"))
            else:
                print(f"[warn] Unexpected JSON type in {f}: {type(obj)}", file=sys.stderr)
        except Exception as e:
            print(f"[warn] failed to read {f}: {e}", file=sys.stderr)

    # case B: single file followers.json (if present)
    single = data_dir / "followers.json"
    if single.exists():
        try:
            obj = json.loads(single.read_text(encoding="utf-8"))
            if isinstance(obj, dict):
                if "relationships_followers" in obj:
                    for entry in obj.get("relationships_followers", []):
                        add_from_string_list(entry.get("string_list_data"))
                elif "string_list_data" in obj:
                    add_from_string_list(obj.get("string_list_data"))
            elif isinstance(obj, list):
                for entry in obj:
                    add_from_string_list(entry.get("string_list_data"))
        except Exception as e:
            print(f"[warn] failed to read {single}: {e}", file=sys.stderr)

    return followers


def load_following(data_dir: Path) -> set[str]:
    path = data_dir / "following.json"
    following = set()
    if not path.exists(): return following
    obj = json.loads(path.read_text(encoding="utf-8"))
    for it in obj.get("relationships_following", []):
        title = (it.get("title") or "").strip().lstrip("@").lower()
        if title: following.add(title)
    return following

def load_pending(data_dir: Path) -> set[str]:
    pending = set()
    for name, key in [
        ("pending_follow_requests.json", "relationships_follow_requests_sent"),
        ("recent_follow_requests.json", "relationships_permanent_follow_requests"),
    ]:
        p = data_dir / name
        if not p.exists(): continue
        obj = json.loads(p.read_text(encoding="utf-8"))
        for blk in obj.get(key, []):
            for it in blk.get("string_list_data", []):
                v = it.get("value")
                if v: pending.add(v.strip().lstrip("@").lower())
    return pending

def write_csv(path: Path, rows: list[dict]):
    if not rows:
        print("[info] nothing to write")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
    print(f"[ok] wrote {path}")