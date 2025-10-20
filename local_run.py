'''
Example usage:
    python3 local_run.py
'''
from utils import write_csv, load_followers, load_following, load_pending
import argparse
from pathlib import Path

def main():
    ap = argparse.ArgumentParser(description="Find Instagram accounts you follow that don't follow back (from data export).")
    ap.add_argument("--data-dir", default="connections/followers_and_following",
                    help="folder containing followers_*.json, following.json, etc.")
    ap.add_argument("--csv", default="", help="optional path to save CSV (e.g., out/unfollowers.csv)")
    ap.add_argument("--show", type=int, default=50, help="print first N results in console")
    args = ap.parse_args()

    data_dir = Path(args.data_dir)
    followers = load_followers(data_dir)                 # who follows you
    following = load_following(data_dir)                 # who you follow
    pending   = load_pending(data_dir)                   # requests you sent

    not_following_back = sorted(following - followers)
    fans_only          = sorted(followers - following)
    mutuals            = sorted(followers & following)

    # annotate pending requests
    pending_set = set(pending)
    rows = []
    for u in not_following_back:
        rows.append({
            "username": u,
            "status": "pending" if u in pending_set else "not-following-back",
            "profile": f"https://www.instagram.com/{u}",
        })

    print(f"\n=== Summary ===")
    print(f"Followers: {len(followers)} | Following: {len(following)}")
    print(f"Mutuals: {len(mutuals)} | Not following back: {len(not_following_back)} | Fans only: {len(fans_only)}")

    if not_following_back:
        print(f"\n=== Not following back (showing first {args.show}) ===")
        for u in not_following_back[:args.show]:
            tag = " (pending)" if u in pending_set else ""
            print(f"- {u}{tag}")

    if args.csv:
        write_csv(Path(args.csv), rows)

if __name__ == "__main__":
    main()
