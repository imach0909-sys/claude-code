#!/usr/bin/env python3
"""Esutech Daily News Bot - Fetches curated news and posts to Slack #industry-news"""

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import feedparser
import anthropic
from slack_sdk import WebClient

JST = timezone(timedelta(hours=9))
SLACK_CHANNEL_ID = "C0B470FJNUF"
POSTED_NEWS_FILE = "data/posted_news.json"
MAX_STORED_URLS = 700  # ~100/day × 7 days

NEWS_QUERIES = [
    # 1. 日本・ベトナム国交関係
    "日本 ベトナム 外交 国交 関係",
    "Japan Vietnam diplomatic relations",
    # 2. 日本のベトナム人材育成
    "ベトナム 技能実習 特定技能 日本",
    "ベトナム人材 日本 育成 受け入れ",
    # 3. 日本産業ニュース
    "日本 産業 製造業 経済 大手企業",
    "日本企業 経営 ニュース",
    # 4. AI・ロボティクス
    "AI 人工知能 日本 最新",
    "ロボット 自動化 日本 ニュース",
    "artificial intelligence robotics Japan",
]

CATEGORY_EMOJIS = {
    "日本・ベトナム国交関係": "🇯🇵🇻🇳",
    "日本のベトナム人材育成": "👥",
    "日本産業ニュース": "🏭",
    "AI・ロボティクス": "🤖",
}


def fetch_google_news(query: str) -> list[dict]:
    import urllib.parse
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(query)}&hl=ja&gl=JP&ceid=JP:ja"
    feed = feedparser.parse(url)
    cutoff = datetime.now(JST) - timedelta(hours=36)
    articles = []
    for entry in feed.entries[:15]:
        try:
            pub = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc).astimezone(JST)
            if pub < cutoff:
                continue
            articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": getattr(entry, "summary", ""),
                "published": pub.isoformat(),
                "source": getattr(entry, "source", {}).get("title", ""),
            })
        except Exception:
            continue
    return articles


def load_posted_urls() -> set[str]:
    if os.path.exists(POSTED_NEWS_FILE):
        with open(POSTED_NEWS_FILE, encoding="utf-8") as f:
            return set(json.load(f).get("urls", []))
    return set()


def save_posted_urls(existing: set[str], new: set[str]) -> None:
    os.makedirs(os.path.dirname(POSTED_NEWS_FILE), exist_ok=True)
    combined = list(existing | new)
    if len(combined) > MAX_STORED_URLS:
        combined = combined[-MAX_STORED_URLS:]
    with open(POSTED_NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {"urls": combined, "last_updated": datetime.now(JST).isoformat()},
            f, ensure_ascii=False, indent=2,
        )


def collect_articles(posted_urls: set[str]) -> list[dict]:
    all_articles: list[dict] = []
    seen_links: set[str] = set()
    for query in NEWS_QUERIES:
        for article in fetch_google_news(query):
            link = article["link"]
            if link not in seen_links and link not in posted_urls:
                all_articles.append(article)
                seen_links.add(link)
    return all_articles


def select_and_translate(articles: list[dict]) -> list[dict]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now(JST).strftime("%Y年%m月%d日")

    prompt = f"""あなたはEsutechのニュースキュレーターです。
Esutechは日本とベトナムをつなぐ人材育成・テクノロジー事業を展開する会社です。

本日（{today}）の記事候補から、重要度の高い順に最大10件を選んでください。

【選定優先度】
1. 日本とベトナムの国交・外交関係ニュース
2. 日本のベトナム人材育成制度（技能実習・特定技能・留学等）
3. 日本産業界の重大ニュース（大手企業・経済政策・製造業等）
4. AI・ロボティクスの重要ニュース

【ルール】
- 同じ出来事の記事は1件にまとめること（続報はOK）
- 前日までに既出の内容は除外（候補はすでにフィルタ済み）
- JSONのみ出力（前後のテキスト不要）

【出力フォーマット（JSON配列）】
[
  {{
    "rank": 1,
    "category": "カテゴリ（日本・ベトナム国交関係 / 日本のベトナム人材育成 / 日本産業ニュース / AI・ロボティクス のいずれか）",
    "title_ja": "日本語タイトル（簡潔に）",
    "title_vi": "Tiêu đề tiếng Việt",
    "summary_ja": "日本語要約（2〜3文）",
    "summary_vi": "Tóm tắt tiếng Việt (2〜3 câu)",
    "source": "媒体名",
    "link": "元記事URL"
  }}
]

記事候補:
{json.dumps(articles[:60], ensure_ascii=False, indent=2)}
"""

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=5000,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text

    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        print("ERROR: Could not parse Claude response:\n", raw, file=sys.stderr)
        sys.exit(1)
    return json.loads(match.group())


def build_slack_blocks(news_items: list[dict]) -> list[dict]:
    today = datetime.now(JST).strftime("%Y年%m月%d日（%A）")
    # strftime weekday is English; map to Japanese
    weekday_ja = ["月", "火", "水", "木", "金", "土", "日"][datetime.now(JST).weekday()]
    today = datetime.now(JST).strftime(f"%Y年%m月%d日（{weekday_ja}曜日）")

    blocks: list[dict] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📰 Esutech デイリーニュース｜Tin Tức Hàng Ngày",
                "emoji": True,
            },
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": (
                        f"*{today}*　|　本日の厳選ニュース {len(news_items)} 件"
                        f"　|　{len(news_items)} tin tức được chọn lọc hôm nay"
                    ),
                }
            ],
        },
        {"type": "divider"},
    ]

    for item in news_items:
        emoji = CATEGORY_EMOJIS.get(item.get("category", ""), "📌")
        cat = item.get("category", "")
        source = item.get("source") or "記事を読む"
        link = item["link"]
        rank = item["rank"]

        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{emoji} *{rank}. {cat}*\n"
                    f"*🇯🇵 {item['title_ja']}*\n"
                    f"{item['summary_ja']}\n\n"
                    f"*🇻🇳 {item['title_vi']}*\n"
                    f"{item['summary_vi']}\n\n"
                    f"🔗 <{link}|{source}>"
                ),
            },
        })
        blocks.append({"type": "divider"})

    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "_Powered by Esutech News Bot | 毎朝7:00配信_",
            }
        ],
    })
    return blocks


def post_to_slack(blocks: list[dict]) -> None:
    client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
    today = datetime.now(JST).strftime("%Y年%m月%d日")
    client.chat_postMessage(
        channel=SLACK_CHANNEL_ID,
        text=f"📰 Esutech デイリーニュース {today}",
        blocks=blocks,
    )


def main() -> None:
    print("Loading previously posted URLs...")
    posted_urls = load_posted_urls()

    print("Fetching articles from news feeds...")
    articles = collect_articles(posted_urls)
    print(f"  {len(articles)} new candidate articles found")

    if not articles:
        print("No new articles found today. Skipping post.")
        return

    print("Selecting and translating with Claude AI...")
    news_items = select_and_translate(articles)
    print(f"  {len(news_items)} items selected")

    print("Posting to Slack #industry-news...")
    blocks = build_slack_blocks(news_items)
    post_to_slack(blocks)
    print("  Posted successfully!")

    new_urls = {item["link"] for item in news_items}
    save_posted_urls(posted_urls, new_urls)
    print("  Updated duplicate-check history")


if __name__ == "__main__":
    main()
