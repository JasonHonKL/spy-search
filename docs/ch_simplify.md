# Spy Search 中文版说明

## 项目简介

**Spy Search** 是一个智能搜索框架，旨在提供比现有网页搜索代理更快速高效的日常搜索体验。

相比Manus等月费$200的商业解决方案，Spy Search基于开源模型提供经济高效的替代方案，同时保持出色的性能表现。
当前版本搜索速度较慢，但能生成长篇一致性报告(约2000字)并整合最新信息！此问题将在v1.0版本中解决。

---

## 发展路线
**最新动态**: 2025-06-10 Spy-searcher 刚刚发布 v0.3 版本！

---

## 安装指南

1. 首先克隆仓库：
```shell
git clone https://github.com/JasonHonKL/spy-search.git
cd spy-search
```

2. 运行安装脚本：
```shell
python setup.py
```

3. 如需使用API，请在.env文件中添加您的API密钥。目前支持：
- OpenAI
- Claude
- Gork
- Deepseek

若使用ollama则无需配置

4. 配置config.json文件，可参考以下模板：
```json
{
    "provider": "ollama",
    "model": "deepseek-r1:7b",
    "agents": [
        "reporter"
    ]
}
```

5. 构建并运行Docker容器：
```shell
docker build -t spy-searcher .   
docker run -p 8000:8000 -p 8080:8080 spy-searcher
```

完成上述步骤后，即可访问：
[http://localhost:8000](http://localhost:8080)

---

## 社区支持
[加入Discord社区](https://discord.gg/rrsMgBdJJt)

---

## 使用示例

- [示例报告(HTML格式)](./docs/examples/example_report.html)

![搜索示例](./docs/examples/example_search.png)

## 演示视频

观看YouTube演示视频：

[![演示视频](https://img.youtube.com/vi/Dgb33BHtRwQ/0.jpg)](https://youtu.be/Dgb33BHtRwQ)

---

## 贡献指南

欢迎社区贡献！参与方式如下：

### 提交Pull Request

- 我们欢迎修复bug、添加功能或改进文档的PR
- 请确保您的PR：
  - 基于最新的main分支
  - 包含清晰的描述和测试说明
  - 通过所有自动化测试

提交后，维护人员将进行审核并提供反馈

### 提交Issue

- 欢迎提交bug报告、功能请求或问题咨询
- 提交issue时请包含：
  - 清晰的标题
  - 问题重现步骤(针对bug)
  - 预期与实际行为
  - 相关环境/版本信息

维护人员将及时处理您的issue并进行分类讨论

---

## 致谢

感谢大家的支持！您的贡献让这个项目变得更好 :)

[![Star历史记录](https://api.star-history.com/svg?repos=JasonHonKL/spy-search&type=Date)](https://star-history.com/#JasonHonKL/spy-search&Date)
