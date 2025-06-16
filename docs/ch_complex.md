# 间谍搜索 繁體中文版說明

## 專案簡介

**Spy Search** 是一個智能搜索框架，旨在提供比現有網頁搜索代理更快速高效的日常搜索體驗。

相比Manus等月費$200的商業解決方案，Spy Search基於開源模型提供經濟高效的替代方案，同時保持出色的性能表現。
當前版本搜索速度較慢，但能生成長篇一致性報告(約2000字)並整合最新資訊！此問題將在v1.0版本中解決。

---

## 發展路線
**最新動態**: 2025-06-10 Spy-searcher 剛剛發佈 v0.3 版本！

---

## 安裝指南

1. 首先克隆倉庫：
```shell
git clone https://github.com/JasonHonKL/spy-search.git
cd spy-search
```

2. 運行安裝腳本：
```shell
python setup.py
```

3. 如需使用API，請在.env文件中添加您的API密鑰。目前支援：
- OpenAI
- Claude
- Gork
- Deepseek

若使用ollama則無需配置

4. 配置config.json文件，可參考以下模板：
```json
{
    "provider": "ollama",
    "model": "deepseek-r1:7b",
    "agents": [
        "reporter"
    ]
}
```

5. 構建並運行Docker容器：
```shell
docker build -t spy-searcher .   
docker run -p 8000:8000 -p 8080:8080 spy-searcher
```

完成上述步驟後，即可訪問：
[http://localhost:8000](http://localhost:8080)

---

## 社群支援
[加入Discord社群](https://discord.gg/rrsMgBdJJt)

---

## 使用範例

- [範例報告(HTML格式)](./docs/examples/example_report.html)

![搜索範例](./docs/examples/example_search.png)

## 示範影片

觀看YouTube示範影片：

[![示範影片](https://img.youtube.com/vi/Dgb33BHtRwQ/0.jpg)](https://youtu.be/Dgb33BHtRwQ)

---

## 貢獻指南

歡迎社群貢獻！參與方式如下：

### 提交Pull Request

- 我們歡迎修復bug、添加功能或改進文件的PR
- 請確保您的PR：
  - 基於最新的main分支
  - 包含清晰的描述和測試說明
  - 通過所有自動化測試

提交後，維護人員將進行審核並提供回饋

### 提交Issue

- 歡迎提交bug報告、功能請求或問題諮詢
- 提交issue時請包含：
  - 清晰的標題
  - 問題重現步驟(針對bug)
  - 預期與實際行為
  - 相關環境/版本資訊

維護人員將及時處理您的issue並進行分類討論

---

## 致謝

感謝大家的支持！您的貢獻讓這個專案變得更好 :)

[![Star歷史記錄](https://api.star-history.com/svg?repos=JasonHonKL/spy-search&type=Date)](https://star-history.com/#JasonHonKL/spy-search&Date)
