import os
import re
import json
import hashlib
from datetime import datetime, timezone, timedelta

import feedparser
import git

RSS_URL = "https://api.velog.io/rss/@yura103"
REPO_PATH = "."
POSTS_DIR = os.path.join(REPO_PATH, "velog-posts")

STATE_FILE = ".velog_sync_state.json"
BOOTSTRAP_DAYS = 14  # 최초 1회 실행 시, 최근 14일만(너무 과거 풀백업 방지)

def safe_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r'[\\/:*?"<>|]', "-", name)
    name = re.sub(r"[\x00-\x1f\x7f]", "", name)
    name = re.sub(r"\s+", " ", name).strip()
    name = name.rstrip(" .")
    return name or "untitled"

def short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]

def parse_entry_dt(entry):
    for key in ("published_parsed", "updated_parsed"):
        v = getattr(entry, key, None)
        if v:
            return datetime(*v[:6], tzinfo=timezone.utc)
    return None

def entry_content(entry) -> str:
    for key in ("summary", "description"):
        v = getattr(entry, key, None)
        if v:
            return v
    return ""

def make_markdown(entry) -> str:
    title = (getattr(entry, "title", "") or "Untitled").strip()
    link = (getattr(entry, "link", "") or "").strip()
    dt = parse_entry_dt(entry)
    dt_str = dt.strftime("%Y-%m-%d %H:%M:%S UTC") if dt else ""
    body = entry_content(entry)

    lines = []
    lines.append(f"# {title}")
    lines.append("")
    if dt_str:
        lines.append(f"- Date: {dt_str}")
    if link:
        lines.append(f"- Velog: {link}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(body if body else "_(No content in RSS feed)_")
    lines.append("")
    return "\n".join(lines)

def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def main():
    if "YOUR_VELOG_ID" in RSS_URL:
        raise RuntimeError("RSS_URL의 YOUR_VELOG_ID를 실제 Velog 아이디로 바꿔줘!")

    os.makedirs(POSTS_DIR, exist_ok=True)
    repo = git.Repo(REPO_PATH)

    feed = feedparser.parse(RSS_URL)
    entries = getattr(feed, "entries", []) or []
    if not entries:
        print("❌ RSS entries가 없어요. RSS_URL 확인!")
        return

    # 최신순 정렬
    entries.sort(key=lambda e: parse_entry_dt(e) or datetime(1970,1,1,tzinfo=timezone.utc), reverse=True)

    state = load_state()
    last_iso = state.get("last_synced_utc")

    if last_iso:
        last_synced = datetime.fromisoformat(last_iso.replace("Z", "+00:00"))
    else:
        last_synced = datetime.now(timezone.utc) - timedelta(days=BOOTSTRAP_DAYS)

    selected = []
    for e in entries:
        dt = parse_entry_dt(e)
        if dt and dt > last_synced:
            selected.append(e)

    if not selected:
        print("✅ 새로 가져올 글이 없어요.")
        return

    changed = 0
    newest_dt = None

    for e in selected:
        title = (getattr(e, "title", "") or "Untitled").strip()
        link = (getattr(e, "link", "") or "").strip()
        dt = parse_entry_dt(e)

        base = safe_filename(title)
        if link:
            base = f"{base}-{short_hash(link)}"
        path = os.path.join(POSTS_DIR, f"{base}.md")

        if os.path.exists(path):
            continue

        with open(path, "w", encoding="utf-8") as f:
            f.write(make_markdown(e))

        changed += 1
        if dt and (newest_dt is None or dt > newest_dt):
            newest_dt = dt

    if changed == 0:
        print("✅ 파일 변화 없음(이미 저장된 글).")
        return

    # state 업데이트
    if newest_dt:
        state["last_synced_utc"] = newest_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        save_state(state)

    repo.git.add("velog-posts")
    repo.git.add(STATE_FILE)
    print(f"✅ {changed}개 새 글 저장 완료 (commit은 workflow에서 처리)")


if __name__ == "__main__":
    main()
