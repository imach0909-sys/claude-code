#!/usr/bin/env python3
"""
Esutech Daily News Bot
Fetches news on Japan-Vietnam relations, talent development,
Japanese industry, and AI/Robotics, posts bilingual JP/VI summary to Slack.
"""

import json
import os
import re
import time
from datetime import datetime, timedelta, timezone

import feedparser
import requests
from anthropic import Anthropic
from slack_sdk import WebClient

SLACK_CHANNEL_ID = "C0B470FJNUF"
JST = timezone(timedelta(hours=9))

NEWS_QUERIES = [
    {
        "query": "日本 ベトナム 国交 外交 関係",
        "category": "🇯🇵🇻🇳 日越国交・外交 / Quan hệ ngoại giao Nhật-Việt",
        "max": 3,
    },
    {
        "query": "ベトナム 人材 日本 育成 技能実習 特定技能 留学",
        "category": "👥 日本のベトナム人材育成 / Đào tạo nhân lực Việt tại Nhật",
        "max": 2,
    },
    {
        "query": "日本 産業 製造業 経済 大手企業",
        "category": "🏭 日本産業ニュース / Tin tức công nghiệp Nhật Bản",
        "max": 2,
    },
    {
        "query": "AI 人工知能 ロボット 技術 最新",
        "category": "🤖 AI・ロボティクス / AI & Robotics",
        "max": 3,
    },
]


def fetch_google_news(query: str, max_results: int = 5) -> list[dict]:
    """Fetch recent articles from Google News RSS."""
    encoded = requests.utils.quote(query)
    url = f"https://news.google.com/rss/search?q={encoded}&hl=ja&gl=JP&ceid=JP:ja"

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"  RSS fetch error: {e}")
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(hours=48)
    articles = []

    for entry in feed.entries:
        if len(articles) >= max_results:
            break
        try:
            pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            if pub_dt < cutoff:
                continue
        except (AttributeError, TypeError):
            pass

        articles.append(
            {
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", "")[:600],
                "published": entry.get("published", ""),
            }
        )

    return articles


def get_recent_posted_urls(client: WebClient, channel_id: str) -> set[str]:
    """Read last 24h of Slack messages and extract URLs to filter duplicates."""
    oldest = str((datetime.now(timezone.utc) - timedelta(hours=24)).timestamp())
    try:
        resp = client.conversations_history(channel=channel_id, oldest=oldest, limit=100)
        urls = set()
        for msg in resp.get("messages", []):
            found = re.findall(r'https?://[^\s|>\)]+', msg.get("text", ""))
            urls.update(found)
        return urls
    except Exception as e:
        print(f"  Could not read Slack history: {e}")
        return set()


def summarize_and_translate(anthropic: Anthropic, articles: list[dict]) -> list[dict]:
    """Use Claude to summarize each article in Japanese and translate to Vietnamese."""
    if not articles:
        return []

    articles_text = ""
    for i, art in enumerate(articles, 1):
        articles_text += (
            f"\n{i}.\nタイトル: {art['title']}\n"
            f"URL: {art['link']}\n"
            f"内容: {art['summary']}\n"
        )

    prompt = f"""以下のニュース記事を処理してください。

各記事について以下を作成してください：
1. 記事タイトルの日本語（元のまま）
2. 記事タイトルのベトナム語翻訳
3. 日本語要約（2〜3文、読者が内容を把握できる簡潔な要約）
4. ベトナム語翻訳（日本語要約の翻訳）

必ず以下のJSON配列のみを返してください（コードブロックなし）：
[
  {{
    "title_ja": "日本語タイトル",
    "title_vi": "Tiêu đề tiếng Việt",
    "summary_ja": "日本語要約",
    "summary_vi": "Tóm tắt tiếng Việt",
    "url": "元のURL"
  }}
]

記事：
{articles_text}"""

    try:
        response = anthropic.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.content[0].text.strip()
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception as e:
        print(f"  Claude API error: {e}")
    return []


def build_slack_message(date_str: str, categorized: list[dict]) -> str:
    """Build a formatted bilingual Slack message."""
    lines = [
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📰 *Esutech Daily News* | {date_str}",
        "日越バイリンガル / Song ngữ Nhật-Việt",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
    ]

    count = 0
    for cat_data in categorized:
        articles = cat_data.get("articles", [])
        if not articles:
            continue
        lines.append(f"\n*{cat_data['category']}*")
        for art in articles:
            count += 1
            lines.append(
                f"\n*{count}. {art['title_ja']}*\n"
                f"　_{art['title_vi']}_\n"
                f"\n　📌 {art['summary_ja']}\n"
                f"　{art['summary_vi']}\n"
                f"　🔗 <{art['url']}|詳細を読む / Đọc thêm>"
            )

    lines.append(
        f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"本日 {count} 件配信 / Hôm nay {count} bài viết"
    )
    return "\n".join(lines)


def main():
    slack_token = os.environ["SLACK_BOT_TOKEN"]
    anthropic_key = os.environ["ANTHROPIC_API_KEY"]

    slack = WebClient(token=slack_token)
    anthropic = Anthropic(api_key=anthropic_key)

    print("Reading recent Slack posts to detect duplicates...")
    recent_urls = get_recent_posted_urls(slack, SLACK_CHANNEL_ID)
    print(f"  {len(recent_urls)} URLs already posted in last 24h")

    categorized = []
    total = 0

    for query_cfg in NEWS_QUERIES:
        if total >= 10:
            break

        remaining = min(query_cfg["max"], 10 - total)
        print(f"\nFetching: {query_cfg['query']}")

        articles = fetch_google_news(query_cfg["query"], remaining * 3)

        # Filter duplicates
        new_articles = [a for a in articles if a["link"] not in recent_urls][:remaining]
        print(f"  {len(articles)} fetched → {len(new_articles)} new")

        if not new_articles:
            continue

        time.sleep(1)  # Avoid Claude API rate limits
        processed = summarize_and_translate(anthropic, new_articles)

        if processed:
            categorized.append({"category": query_cfg["category"], "articles": processed})
            total += len(processed)

    if total == 0:
        print("\nNo new articles found today. Skipping post.")
        return

    jst_now = datetime.now(JST)
    weekdays_ja = ["月", "火", "水", "木", "金", "土", "日"]
    weekdays_vi = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    wd = jst_now.weekday()
    date_str = (
        f"{jst_now.strftime('%Y年%m月%d日')}（{weekdays_ja[wd]}）"
        f" / {jst_now.strftime('%d/%m/%Y')} ({weekdays_vi[wd]})"
    )

    message = build_slack_message(date_str, categorized)

    print(f"\nPosting {total} articles to Slack...")
    slack.chat_postMessage(channel=SLACK_CHANNEL_ID, text=message, mrkdwn=True)
    print("Done!")


if __name__ == "__main__":
    main()
