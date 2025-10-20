'''
Example usage:
    streamlit run app.py
'''
# app_streamlit.py
from __future__ import annotations
import shutil, tempfile
from pathlib import Path
import pandas as pd
import streamlit as st

# Use your existing helpers
from utils import load_followers, load_following, load_pending

DEFAULT_DIR = Path("connections/followers_and_following").resolve()
BUTTON_IMG = Path("assets/button.png")  # optional banner

st.set_page_config(page_title="Instagram Unfollowers", layout="wide")
st.title("Instagram Unfollowers (Local)")

# Optional banner
if BUTTON_IMG.exists():
    try:
        st.image(str(BUTTON_IMG), use_column_width=False)
    except Exception:
        pass

st.caption("Point to your Instagram export folder (contains `followers_*.json`, `following.json`, etc.) "
           "or upload a ZIP that includes `connections/followers_and_following`.")

# ---- Input method ----
mode = st.radio("Choose input method", ["Folder path (local)", "Upload ZIP"], horizontal=True)

tmp_dir_obj = None
data_dir_path: Path | None = None

if mode == "Folder path (local)":
    data_dir = st.text_input("Data folder path", value=str(DEFAULT_DIR))
    if data_dir:
        data_dir_path = Path(data_dir).expanduser().resolve()
else:
    zip_file = st.file_uploader("Upload your export ZIP", type=["zip"])
    if zip_file is not None:
        tmp_dir_obj = tempfile.TemporaryDirectory()
        extract_root = Path(tmp_dir_obj.name)
        zpath = extract_root / "export.zip"
        zpath.write_bytes(zip_file.read())
        shutil.unpack_archive(str(zpath), str(extract_root))

        # Try to locate followers_and_following folder
        candidate = extract_root / "connections" / "followers_and_following"
        if not candidate.exists():
            for p in extract_root.rglob("followers_and_following"):
                if p.is_dir() and (p / "following.json").exists():
                    candidate = p
                    break
        if candidate.exists():
            data_dir_path = candidate
            st.info(f"Using extracted folder: {data_dir_path}")
        else:
            st.error("Couldn’t find `connections/followers_and_following` inside the ZIP.")

# ---- Options ----
c1, c2, c3 = st.columns([1,1,2])
with c1:
    hide_pending = st.checkbox("Hide pending requests", value=False)
with c2:
    sort_alpha = st.checkbox("Sort A→Z", value=True)
with c3:
    search_filter = st.text_input("Filter usernames (optional)", value="")

scan = st.button("Scan")

def build_df(usernames: set[str], pending: set[str], label_pending=True):
    rows = []
    for u in usernames:
        status = "pending" if (label_pending and u in pending) else (
            "not-following-back" if label_pending else "fan"
        )
        if hide_pending and status == "pending":
            continue
        if search_filter and search_filter.lower() not in u.lower():
            continue
        rows.append({"username": u, "status": status, "profile": f"https://www.instagram.com/{u}"})
    if sort_alpha:
        rows.sort(key=lambda r: r["username"])
    return pd.DataFrame(rows, columns=["username", "status", "profile"])

if scan:
    if data_dir_path is None or not data_dir_path.exists():
        st.error("Please provide a valid folder path or a ZIP with the export.")
    else:
        with st.spinner("Scanning…"):
            followers = load_followers(data_dir_path)
            following = load_following(data_dir_path)
            pending   = load_pending(data_dir_path)

            not_back = following - followers
            fans_only = followers - following
            mutuals  = followers & following

        st.success("Scan complete")
        st.markdown(
            f"**Followers:** {len(followers)} | **Following:** {len(following)} | "
            f"**Mutuals:** {len(mutuals)} | **Not following back:** {len(not_back)} | "
            f"**Fans only:** {len(fans_only)}"
        )

        tab1, tab2, tab3 = st.tabs(["Not following back", "Mutuals", "Fans only"])

        with tab1:
            df1 = build_df(not_back, pending, label_pending=True)
            st.dataframe(df1, use_container_width=True, hide_index=True)
            if not df1.empty:
                st.download_button("Download CSV (not-following-back)",
                                   df1.to_csv(index=False).encode("utf-8"),
                                   "unfollowers_not_back.csv", "text/csv")

        with tab2:
            df2 = build_df(mutuals, pending=False, label_pending=False)
            df2["status"] = "mutual"
            st.dataframe(df2, use_container_width=True, hide_index=True)
            if not df2.empty:
                st.download_button("Download CSV (mutuals)",
                                   df2.to_csv(index=False).encode("utf-8"),
                                   "unfollowers_mutuals.csv", "text/csv")

        with tab3:
            df3 = build_df(fans_only, pending=False, label_pending=False)
            # already “fan”
            st.dataframe(df3, use_container_width=True, hide_index=True)
            if not df3.empty:
                st.download_button("Download CSV (fans-only)",
                                   df3.to_csv(index=False).encode("utf-8"),
                                   "unfollowers_fans_only.csv", "text/csv")

st.caption("Tip: On macOS you can drag a folder into Terminal to paste its full path.")
