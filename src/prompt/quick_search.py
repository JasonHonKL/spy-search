from string import Template
import datetime


template = Template("""
# Search Results Summary
**Timestamp:** $timestamp

---

## User Query
> $query

---

## Overall Summary

<<Generate a concise overall summary of the combined search results here>>

---

## Detailed Search Results

$results

---

## Instructions for Response

1. Begin your response by printing the current date and time in the format **YYYY-MM-DD HH:MM:SS** as a timestamp.
2. Generate a brief overall summary of all search results combined (4-5 sentences) where indicated above.
3. Then, list each search result with:  
   - A numbered clickable link in Markdown format: `[Title](URL)`  
   - A concise, relevant summary immediately below the link.
4. Ensure each summary includes exactly one clickable Markdown URL — no duplicates or raw URLs outside the link.
5. Keep all summaries clear, professional, and focused on the query.
6. Avoid unnecessary filler; keep responses concise.
7. Use APA-style inline citations when appropriate.
8. Format your full response as Markdown, starting with the timestamp and overall summary, followed by the numbered list of results.

---

**Example Output:**

**Timestamp:** 2025-06-14 14:23:05

### Overall Summary

The Example Domain is a reserved domain used for illustrative examples in documents. It allows free use without prior permission.

### Detailed Search Results

1. [Example Domain](https://example.com)  
This domain is intended for use in illustrative examples within documents. You may use it freely without prior coordination or permission (Example Domain, n.d.) [Example Domain](https://example.com).

2. [Another Link](https://another.com)  
Brief summary of content on another link.

---

Your final response must start with the current timestamp, then an overall summary, and finally a numbered list of clickable links with concise summaries in Markdown format.
""")


template_ch = Template("""
# 搜索结果摘要
**时间戳：** $timestamp

---

## 用户查询
> $query

---

## 总体总结

<<请在此处生成所有搜索结果的简明总体总结，4-5句，100-200字，且必须包含APA格式引用>>

---

## 详细搜索结果

$results

---

## 回复说明

1. 回复开头打印当前日期时间，格式 **YYYY-MM-DD HH:MM:SS**，作为时间戳。
2. 在指定位置生成所有结果的简短总体总结(4-5句,100-200字),且必须包含APA格式引用。
3. 列出每条结果：  
    - 编号的Markdown可点击链接:[标题](URL)  
    - 链接下方简明相关摘要。
4. 每个摘要含且仅含一个Markdown链接,无裸露URL。
5. 内容清晰专业，聚焦查询。
6. 避免赘述，简洁明了。
7. 适用时用APA格式引用。
8. 全文Markdown格式:先时间戳和总体总结，再编号结果。

---

**示例输出：**

**时间戳：** 2025-06-14 14:23:05

### 总体总结

Example Domain 是一个专门用作文档示例的保留域名，允许用户在不需提前许可或协调的情况下自由使用该域名，适合在各种说明性文档中引用（Example Domain, n.d.）。

### 详细搜索结果

1. [Example Domain](https://example.com)  
该域名用于文档中的示例展示，用户可无需许可自由使用（Example Domain, n.d.）[Example Domain](https://example.com)。

2. [Another Link](https://another.com)  
另一链接内容简要摘要。

---

最终回复从时间戳开始，接总体总结，后跟编号链接及简洁摘要，全部为Markdown格式，且总结部分必须含APA格式引用。
""")
import json

def load_config_language(config_path='./config.json'):
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('language', 'en')
    except Exception:
        # 默认英文
        return 'en'

def quick_search_prompt(query, data, timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    language = load_config_language()
    if language == 'ch':
        return template_ch.substitute(timestamp=timestamp, query=query, results=data)
    else:
        return template.substitute(timestamp=timestamp, query=query, results=data)