# Spy Search 日本語版ドキュメント

## プロジェクト概要

**Spy Search**は、既存のウェブ検索エージェントを上回る性能を目指したインテリジェント検索フレームワークです。日常的な検索をより速く、効率的に行うことに重点を置いています。

Manusのような月額$200の商用ソリューションと比較して、Spy Searchはオープンソースモデルを活用することで、性能を犠牲にすることなくコスト効率の良い代替手段を提供します。
現在のバージョンでは検索速度がやや遅いですが、最新情報を統合した長文の一貫性のあるレポート（約2000語）を生成できます！この問題はv1.0リリースで解決予定です。

---

## ロードマップ
**ニュース**: 2025-06-10 Spy-searcher v0.3がリリースされました！

---

## インストールガイド

1. まずリポジトリをクローン：
```shell
git clone https://github.com/JasonHonKL/spy-search.git
cd spy-search
```

2. セットアップスクリプトを実行：
```shell
python setup.py
```

3. APIを使用する場合は、.envファイルにAPIキーを追加：
現在サポートしているプロバイダ：
- OpenAI
- Claude
- Gork
- Deepseek

ollamaを使用する場合は設定不要

4. config.jsonファイルを設定（テンプレート例）：
```json
{
    "provider": "ollama",
    "model": "deepseek-r1:7b",
    "agents": [
        "reporter"
    ]
}
```

5. Dockerコンテナをビルドして実行：
```shell
docker build -t spy-searcher .   
docker run -p 8000:8000 -p 8080:8080 spy-searcher
```

上記手順完了後、以下にアクセス可能：
[http://localhost:8000](http://localhost:8080)

---

## コミュニティ
[Discordコミュニティに参加](https://discord.gg/rrsMgBdJJt)

---

## 使用例

- [レポート例（HTML形式）](./docs/examples/example_report.html)

![検索例](./docs/examples/example_search.png)

## デモ動画

YouTubeでデモ動画を視聴：

[![デモ動画](https://img.youtube.com/vi/Dgb33BHtRwQ/0.jpg)](https://youtu.be/Dgb33BHtRwQ)

---

## コントリビューション

コミュニティからの貢献を歓迎します！参加方法：

### プルリクエスト

- バグ修正、新機能追加、ドキュメント改善のPRを歓迎
- PR作成時は以下を確認：
  - 最新のmainブランチを基にしていること
  - 明確な説明とテスト手順を含むこと
  - すべての自動テストに合格していること

メンテナーがレビュー後、フィードバックまたはマージします

### イシュー報告

- バグ報告、機能リクエスト、質問のイシュー作成を歓迎
- イシュー報告時は以下を含めてください：
  - 明確なタイトル
  - 再現手順（バグの場合）
  - 期待される動作と実際の動作
  - 関連する環境/バージョン情報

メンテナーが適切にラベル付けし、問題解決に向けて対応します

---

## 謝辞

皆様のサポートに感謝します！コントリビューションがこのプロジェクトをより良いものにします :)

[![スター履歴](https://api.star-history.com/svg?repos=JasonHonKL/spy-search&type=Date)](https://star-history.com/#JasonHonKL/spy-search&Date)
