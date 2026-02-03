import os
import re
import json
from datetime import datetime, timezone
from collections import defaultdict

import requests

GQL_ENDPOINT = "https://v2.velog.io/graphql"

# ====== README 스타일 옵션 ======
MAX_VISIBLE_PER_SERIES = 5      # 시리즈별 기본 노출 개수
SHOW_LATEST_SECTION = True      # README 상단에 "Latest" 섹션 표시 여부
LATEST_COUNT = 5                # Latest 섹션에 보여줄 글 개수
SHOW_NO_SERIES_SECTION = False  # "시리즈 없음" 섹션 표시 여부(원하면 True)

# README 자동 생성 영역 마커
START_MARK = "<!-- VELOG_SERIES_INDEX:START -->"
END_MARK = "<!-- VELOG_SERIES_INDEX:END -->"

# 리스트 스타일(하이픈 싫다고 해서 •로 통일)
BULLET = "•"

def gql(payload: dict):
    r = requests.post(
        GQL_ENDPOINT,
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        raise RuntimeError(data["errors"])
    return data["data"]

def iso_dt(s: str):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None

def fetch_series_list(username: str):
    payload = {
        "operationName": "UserSeriesList",
        "variables": {"username": username},
        "query": (
            "query UserSeriesList($username: String!) {"
            "  user(username: $username) {"
            "    series_list { name url_slug posts_count updated_at }"
            "  }"
            "}"
        ),
    }
    data = gql(payload)
    user = data.get("user") or {}
    return user.get("series_list") or []

def fetch_all_posts(username: str, limit: int = 50):
    posts = []
    cursor = None
    while True:
        payload = {
            "operationName": "Posts",
            "variables": {"username": username, "cursor": cursor, "limit": limit},
            "query": (
                "query Posts($cursor: ID, $username: String, $temp_only: Boolean, $tag: String, $limit: Int) {"
                "  posts(cursor: $cursor, username: $username, temp_only: $temp_only, tag: $tag, limit: $limit) {"
                "    id title url_slug released_at"
                "  }"
                "}"
            ),
        }
        data = gql(payload)
        page = data.get("posts") or []
        if not page:
            break
        posts.extend(page)
        cursor = page[-1]["id"]
        if len(page) < limit:
            break
    return posts

def read_post_series(username: str, url_slug: str):
    payload = {
        "operationName": "ReadPost",
        "variables": {"username": username, "url_slug": url_slug},
        "query": (
            "query ReadPost($username: String, $url_slug: String) {"
            "  post(username: $username, url_slug: $url_slug) {"
            "    series { name url_slug }"
            "  }"
            "}"
        ),
    }
    data = gql(payload)
    post = data.get("post")
    if not post:
        return None
    return post.get("series")

def replace_block(readme: str, block: str):
    pattern = re.compile(re.escape(START_MARK) + r".*?" + re.escape(END_MARK), re.DOTALL)
    replacement = f"{START_MARK}\n{block}\n{END_MARK}"
    if pattern.search(readme):
        return pattern.sub(replacement, readme)
    return readme.rstrip() + "\n\n" + replacement + "\n"

def md_link(text: str, url: str) -> str:
    return f"[{text}]({url})"

def build_block(username: str, series_list: list, posts: list, series_by_post: dict):
    grouped = defaultdict(list)
    no_series = []

    all_items = []  # Latest 섹션용

    for p in posts:
        slug = p["url_slug"]
        title = (p.get("title") or "").strip()
        dt = iso_dt(p.get("released_at", "")) or datetime(1970, 1, 1, tzinfo=timezone.utc)
        link = f"https://velog.io/@{username}/{slug}"

        item = {"title": title, "link": link, "dt": dt}
        all_items.append(item)

        s = series_by_post.get(slug)
        if s and s.get("url_slug"):
            grouped[s["url_slug"]].append(item)
        else:
            no_series.append(item)

    # 정렬: 최신 먼저
    for k in list(grouped.keys()):
        grouped[k].sort(key=lambda x: x["dt"], reverse=True)
    no_series.sort(key=lambda x: x["dt"], reverse=True)
    all_items.sort(key=lambda x: x["dt"], reverse=True)

    # 시리즈 표시 이름/순서
    name_by_slug = {s["url_slug"]: s["name"] for s in series_list if s.get("url_slug")}
    ordered = [s["url_slug"] for s in series_list if s.get("url_slug")]
    for k in grouped.keys():
        if k not in ordered:
            ordered.append(k)

    lines = []
    lines.append("## 📚 Velog Archive")
    lines.append("")
    # 깔끔하게 작게 표시(‘로그 느낌’ 제거)
    now_kst = datetime.now(timezone.utc).astimezone(timezone.utc)  # 표기용(UTC)
    lines.append(f"<sub>Auto-updated • published posts only</sub>")
    lines.append("")

    # Latest 섹션
    if SHOW_LATEST_SECTION and all_items:
        lines.append("### ✨ Latest")
        lines.append("")
        for it in all_items[:LATEST_COUNT]:
            lines.append(f"{BULLET} {md_link(it['title'], it['link'])}")
        lines.append("")
        lines.append("---")
        lines.append("")

    def render_series_section(series_name: str, items: list, series_slug: str | None):
        # 섹션 제목
        lines.append(f"### {series_name}")

        # 시리즈 전체 보기 링크(문장 대신 아이콘 링크)
        if series_slug:
            series_url = f"https://velog.io/@{username}/series/{series_slug}"
            lines.append(f'<a href="{series_url}">🔗 View the full series</a>')
        lines.append("")

        head = items[:MAX_VISIBLE_PER_SERIES]
        tail = items[MAX_VISIBLE_PER_SERIES:]

        for it in head:
            lines.append(f"{BULLET} {md_link(it['title'], it['link'])}")

        if tail:
            lines.append("")
            lines.append("<details>")
            lines.append("<summary>더보기</summary>")
            lines.append("")
            for it in tail:
                lines.append(f"{BULLET} {md_link(it['title'], it['link'])}")
            lines.append("")
            lines.append("</details>")

        lines.append("")
        lines.append("---")
        lines.append("")

    # 시리즈별 렌더
    for series_slug in ordered:
        items = grouped.get(series_slug)
        if not items:
            continue
        series_name = name_by_slug.get(series_slug, series_slug)
        render_series_section(series_name, items, series_slug)

    # 시리즈 없음(원하면)
    if SHOW_NO_SERIES_SECTION and no_series:
        render_series_section("Misc", no_series, None)

    # 마지막 구분선 제거(끝이 ---로 끝나는 거 싫으면)
    if lines and lines[-1] == "":
        # 뒤에서 "---\n\n" 패턴 제거
        # 안전하게 끝부분 정리
        while lines and lines[-1] == "":
            lines.pop()
        if lines and lines[-1] == "---":
            lines.pop()
        lines.append("")

    return "\n".join(lines).rstrip()

def main():
    username = os.environ.get("VELOG_USERNAME")
    if not username:
        raise RuntimeError("VELOG_USERNAME 환경변수가 필요해요.")

    # ReadPost 캐시
    cache_file = ".velog_series_cache.json"
    cache = {}
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)

    series_list = fetch_series_list(username)
    posts = fetch_all_posts(username)

    series_by_post = {}
    changed_cache = False

    for p in posts:
        slug = p["url_slug"]
        if slug in cache:
            series_by_post[slug] = cache[slug]
            continue

        s = read_post_series(username, slug)
        cache[slug] = {"name": s.get("name"), "url_slug": s.get("url_slug")} if s else None
        series_by_post[slug] = cache[slug]
        changed_cache = True

    if changed_cache:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)

    if not os.path.exists("README.md"):
        with open("README.md", "w", encoding="utf-8") as f:
            f.write("# Velog Archive\n\n")

    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read()

    block = build_block(username, series_list, posts, series_by_post)
    new_readme = replace_block(readme, block)

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_readme)

    print("✅ README 시리즈 목차 갱신 완료")

if __name__ == "__main__":
    main()
