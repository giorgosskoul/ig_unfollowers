# 📸 Instagram Unfollowers App

This is a **Python (3.9+) Streamlit** application that helps you check which Instagram accounts you follow but do not follow you back.  
It works **offline** using your downloaded Instagram data — no login or credentials required.

---

## 🧠 How it works

Instagram allows you to export your own data (followers, following, etc.) in **JSON format**.  
This app parses that information locally and shows:
- ✅ Mutuals (you follow each other)
- 🚫 Not following back
- 💕 Fans only (they follow you, but you don’t follow them)

---

## 📥 Getting your Instagram data

Follow these steps carefully:

1. Go to **Instagram → Settings → Privacy Center**  
   (found under **More info and support**).
2. Choose **Export Your Information** → click **Get Started**.
3. In the new page, click **Export your Information** again → then **Download or transfer information**.
4. Select your **Instagram account**.
5. Under **How much information do you want?**, choose **Some of your information**.
6. In the next tab, under **Connections**, select **Followers and Following** only.
7. Choose **Download to device**.
8. For **Data range**, pick **All time** (not “Last year”).
9. Choose **Format → JSON** (not HTML).
10. Press **Create files**.

After a few minutes, Instagram will send you an email titled *“Your information is ready to download.”*  
Download the ZIP file from that email.

---

## 📁 Placing your data

When you unzip the file from Instagram, you’ll get a folder named **`connections`**, which contains another folder:
```
connections/
└─ followers_and_following/
├─ blocked_profiles.json
├─ close_friends.json
├─ followers_1.json
├─ following.json
├─ hide_story_from.json
├─ pending_follow_requests.json
├─ recent_follow_requests.json
├─ recently_unfollowed_profiles.json
└─ removed_suggestions.json
```

👉 **Move the entire `connections` folder into the root directory of this repository.**

Keep this exact structure — do not rename folders or files.

---

## ⚙️ Installation

Clone or download this repository, then open a terminal inside the project folder.

### 1. (Optional) Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate     # macOS / Linux
# or
.\.venv\Scripts\activate      # Windows
```

### 2. Install Dependencies
```
pip install -r requirements.txt
```

### 3. Run app

``` streamlit run app.py```
or
```python local_run.py```

## Repository Structure Prototype
```
unfollowers-app/
├─ app.py                     # main Streamlit app
├─ utils.py                   # JSON parsing and data helpers
├─ local_run.py               # optional local (non-GUI) runner
├─ requirements.txt
├─ connections/
│  └─ followers_and_following/
│     ├─ followers_1.json
│     ├─ following.json
│     └─ ...
└─ assets/                    # optional (images, icons)
   ├─ app.png
   ├─ app.icns
   ├─ button.png
   └─ app.ico
```

## ⚠️ Current Limitations

- Some “unfollowers” listed may actually be accounts that were deleted or deactivated after you followed them.
- Only part of the list corresponds to real, active accounts.
- The app works fully offline and uses only the JSON export — no API calls or login.

## 💡 Notes

- Tested with Python 3.9, but any version supporting Streamlit ≥1.30 should work.
- Works on macOS, Windows, and Linux.
- You can bundle it as a standalone macOS app using PyInstaller.

## Enjoy finding your unfollowers safely and privately 👀
