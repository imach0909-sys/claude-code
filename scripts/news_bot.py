#!/usr/bin/env python3
"""
Esutech Daily News Bot
Fetches bilingual (JA/VI) news summaries and posts to Slack #industry-news at 7:00 AM JST.

Categories:
  1. Japan-Vietnam diplomatic/economic relations
  2. Vietnam human resource development in Japan
  3. Major Japan industry news
  4. AI and Robotics news
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

import feedparser
import requests
from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
JST = timezone(timedelta(hours=9))
CHANNEL_ID = "C0B470FJNUF"
MAX_NEWS = 10
DATA_FILE = Path(__file__).parent.parent / "data" / "posted_news.json"
WEEKDAYS_JA = ["月", "火", "水", "木", "金", "土", "日"]

SLACK_TOKEN = os.environ["SLACK_BOT_TOKEN"]
anthropic_client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ---------------------------------------------------------------------------
# RSS / Google News sources
# ---------------------------------------------------------------------------
SOURCES = [
    # --- Category 1: Japan-Vietnam relations ---
    "https://news.google.com/rss/search?q=%E6%97%A5%E6%9C%AC+%E3%83%99%E3%83%88%E3%83%8A%E3%83%A0+%E5%9B%BD%E4%BA%A4&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=%E6%97%A5%E8%B6%8A+%E5%A4%96%E4%BA%A4&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=Japan+Vietnam+relations+bilateral&hl=en-US&gl=US&ceid=US:en",
    # --- Category 2: Vietnam HR / training in Japan ---
    "https://news.google.com/rss/search?q=%E3%83%99%E3%83%88%E3%83%8A%E3%83%A0%E4%BA%BA+%E6%8A%80%E8%83%BD%E5%AE%9F%E7%BF%92+%E7%89%B9%E5%AE%9A%E6%8A%80%E8%83%BD&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=%E3%83%99%E3%83%88%E3%83%8A%E3%83%A0+%E4%BA%BA%E6%9D%90+%E8%82%B2%E6%88%90+%E6%97%A5%E6%9C%AC&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=Vietnam+workers+Japan+training+visa+2026&hl=en-US&gl=US&ceid=US:en",
    # --- Category 3: Japan industry ---
    "https://news.google.com/rss/search?q=%E6%97%A5%E6%9C%AC+%E7%94%A3%E6%A5%AD+%E5%A4%A7%E6%89%8B+%E6%B1%BA%E7%AE%97&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=%E6%97%A5%E6%9C%AC+%E7%B5%8C%E6%B8%88+%E6%94%BF%E7%AD%96+%E7%94%A3%E6%A5%AD&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=Japan+industry+economy+corporate+2026&hl=en-US&gl=US&ceid=US:en",
    # --- Category 4: AI and Robotics ---
    "https://news.google.com/rss/search?q=AI+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD+%E3%83%AD%E3%83%9C%E3%83%83%E3%83%88+%E6%97%A5%E6%9C%AC&hl=ja&gl=JP&ceid=JP:ja",
    "https://news.google.com/rss/search?q=AI+robotics+Japan+2026&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=generative+AI+LLM+robot+2026&hl=en-US&gl=US&ceid=US:en",
]

CATEGORY_LABELS = {
    "japan_vietnam": "🇯🇵🇻🇳 日越関係 / Quan hệ Nhật-Việt",
    "vietnam_hr": "👥 ベトナム人材育成 / Phát triển nhân lực Việt Nam",
    "japan_industry": "🏭 日本産業 / Công nghiệp Nhật Bản",
    "ai_robotics": "🤖 AI・ロボティクス / AI & Robot",
}
CATEGORY_ORDER = ["japan_vietnam", "vietnam_hr", "japan_industry", "ai_robotics"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def load_posted_news() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"urls": [], "last_updated": ""}


def save_posted_news(data: dict) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data["urls"] = data["urls"][-300:]  # keep ~1 month rolling window
    data["last_updated"] = datetime.now(JST).isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Fetch articles from RSS feeds
# ---------------------------------------------------------------------------

def fetch_articles() -> list[dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    articles: list[dict] = []
    seen_urls: set[str] = set()

    for url in SOURCES:
        try:
            feed = feedparser.parse(url, agent="EsutechNewsBot/1.0")
            for entry in feed.entries[:15]:
                link = entry.get("link", "").strip()
                if not link or link in seen_urls:
                    continue

                # Date filter
                pub_raw = entry.get("published", "")
                try:
                    pub_dt = parsedate_to_datetime(pub_raw)
                    if pub_dt.tzinfo is None:
                        pub_dt = pub_dt.replace(tzinfo=timezone.utc)
                    if pub_dt < cutoff:
                        continue
                except Exception:
                    pass  # no date → include anyway

                title = strip_html(entry.get("title", ""))
                summary = strip_html(entry.get("summary", ""))[:600]
                source = feed.feed.get("title", "News")

                if title:
                    seen_urls.add(link)
                    articles.append({
                        "title": title,
                        "summary": summary,
                        "url": link,
                        "source": source,
                    })
        except Exception as exc:
            print(f"[warn] fetch failed for {url}: {exc}", file=sys.stderr)
        time.sleep(0.3)

    return articles


# ---------------------------------------------------------------------------
# Claude: select, summarize, translate
# ---------------------------------------------------------------------------

def select_and_translate(articles: list[dict], posted_urls: set[str]) -> dict | None:
    fresh = [a for a in articles if a["url"] not in posted_urls]
    if not fresh:
        return None

    today = datetime.now(JST).strftime("%Y年%m月%d日")
    articles_json = json.dumps(fresh[:60], ensure_ascii=False, indent=2)

    prompt = f"""あなたはEsutechという日越人材ビジネス会社のニュース担当AIです。
今日は{today}です。

以下の記事リストから、会社に最も関連する重要ニュースを最大{MAX_NEWS}件選んでください。

【選択優先順位】
1. 日本とベトナムの国交・外交・経済関係
2. 日本のベトナム人材育成制度（技能実習、特定技能、留学生制度等）
3. 日本の産業界の重要ニュース（大企業動向、経済政策、M&A等）
4. AIとロボティクスの重要ニュース

【厳守事項】
- 同一内容は1件のみ（似た記事はより重要な1件に絞る）
- 関連性が低い記事は除外
- 4カテゴリからバランスよく選択（偏らないこと）
- カテゴリに合致しないものは除外

【出力形式】
以下のJSONのみ出力（説明文・コメント不要）：
{{
  "news_items": [
    {{
      "category": "japan_vietnam" | "vietnam_hr" | "japan_industry" | "ai_robotics",
      "title_ja": "日本語タイトル（40文字以内）",
      "summary_ja": "日本語要約（100〜150文字）",
      "title_vi": "Tiêu đề tiếng Việt（dưới 60 ký tự）",
      "summary_vi": "Tóm tắt tiếng Việt（100〜150 từ）",
      "url": "記事URL",
      "source": "情報源名（短く）"
    }}
  ]
}}

記事リスト：
{articles_json}"""

    response = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.content[0].text.strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start == -1 or end == 0:
        raise ValueError(f"No JSON in Claude response:\n{raw[:300]}")
    return json.loads(raw[start:end])


# ---------------------------------------------------------------------------
# Format Slack message
# ---------------------------------------------------------------------------

def format_message(data: dict) -> str:
    now = datetime.now(JST)
    wd = WEEKDAYS_JA[now.weekday()]
    date_str = now.strftime(f"%Y年%m月%d日（{wd}）")

    lines = [
        f"📰 *Esutech Daily News｜{date_str}*",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
    ]

    by_cat: dict[str, list] = {}
    for item in data.get("news_items", []):
        by_cat.setdefault(item["category"], []).append(item)

    num = 1
    for cat in CATEGORY_ORDER:
        items = by_cat.get(cat, [])
        if not items:
            continue
        label = CATEGORY_LABELS[cat]
        lines.append(f"*{label}*")
        lines.append("")
        for item in items:
            lines.append(f"*{num}. {item['title_ja']}*")
            lines.append(f"　🇯🇵 {item['summary_ja']}")
            lines.append(f"　🇻🇳 {item['summary_vi']}")
            lines.append(f"　🔗 <{item['url']}|{item['source']}>")
            lines.append("")
            num += 1
        lines.append("─" * 48)
        lines.append("")

    lines.append("_Esutech News Bot｜毎朝7:00 JST配信_")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Post to Slack
# ---------------------------------------------------------------------------

def post_to_slack(message: str) -> None:
    resp = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {SLACK_TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        },
        json={
            "channel": CHANNEL_ID,
            "text": message,
            "unfurl_links": False,
            "unfurl_media": False,
        },
        timeout=30,
    )
    resp.raise_for_status()
    result = resp.json()
    if not result.get("ok"):
        raise RuntimeError(f"Slack error: {result.get('error')} — {result}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"[{datetime.now(JST).isoformat()}] Esutech News Bot starting...")

    print("Fetching articles from RSS feeds...")
    articles = fetch_articles()
    print(f"  → {len(articles)} unique articles fetched")

    posted_data = load_posted_news()
    posted_urls = set(posted_data["urls"])
    print(f"  → {len(posted_urls)} previously posted URLs in cache")

    print("Calling Claude to select and translate...")
    result = select_and_translate(articles, posted_urls)

    if not result or not result.get("news_items"):
        print("No new relevant news found. Skipping post.")
        return

    selected = result["news_items"]
    print(f"  → {len(selected)} items selected")

    message = format_message(result)
    print("Posting to Slack #industry-news...")
    post_to_slack(message)
    print("  → Posted successfully!")

    new_urls = [item["url"] for item in selected]
    posted_data["urls"].extend(new_urls)
    save_posted_news(posted_data)
    print(f"  → Cached {len(new_urls)} new URLs. Done.")


if __name__ == "__main__":
    main()
