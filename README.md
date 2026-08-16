# Spy Search

**Spy Search** is an agentic search framework designed to outperform current web search agents with a focus on faster, more efficient daily usage.

While commercial solutions like Manus charge $200 per month, Spy Search leverages open-source models to provide a cost-effective alternative without sacrificing performance.
Currently our searching-speed is quite slow yet we can generate a long length consistent report (around 2000 words) with latest current information! This problem will be tackle after the release of v1.0.

##### [简体中文](./docs/ch_simplify.md)
##### [繁體中文](./docs/ch_complex.md)
##### [日本語](./docs/jap.md)
---

## Roadmap
**News**: 2025-06-10 Spy-searcher has just released v0.3 !

---

## Installation
First you have to clone the repo
```shell
git clone https://github.com/JasonHonKL/spy-search.git
cd spy-search
```

To set up just run
```shell
python setup.py
```

Add your API key in the .env file if you want to use API. Currently we support openAI, Claude, Gork & DeepSeek.

Configure the `config.json` file for your local setup. You can copy the example configuration:

```bash
cp config.example.json config.json
```

Then edit `config.json` to match your environment.

### Ollama

If you use Ollama, here's an example of `config.json`:

```json
{
    "provider": "ollama",
    "model": "qwen3:8b",
    "agents": [
        "reporter"
    ],
    "db": "./local_files/test",
    "base_url": "http://host.docker.internal:11434",
    "language": "en"
}
```

### Docker Build

Build and run the application using Docker. This method is recommended for most users as it handles all dependencies automatically:

```shell
# Build and start the container
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

**Prerequisites:**
- **Docker**: Install from [docker.com](https://www.docker.com/products/docker-desktop/) (includes Docker Compose)
- **Docker Compose**: Usually included with Docker Desktop. If not, install separately:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install docker-compose-plugin

  # Or check if installed
  docker-compose --version
  ```
- **Ollama**: Running locally (if using Ollama provider)
- **Model**: The model specified in your `config.json` available in Ollama (e.g., `qwen3:8b`)

### Updating Configuration (Docker Compose)

Changes to `config.json` are automatically synced and take effect immediately - no restart needed.

Now you can access:
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Frontend**: [http://localhost:8080](http://localhost:8080)

## Community
[Discord](https://discord.gg/rrsMgBdJJt)


## Demo Video

Watch the demo video on YouTube:


https://github.com/user-attachments/assets/3e6ef332-d055-421c-bf0a-5f866ba52b11




[old version video](https://www.youtube.com/watch?v=Dgb33BHtRwQ)

## Contributing

We welcome contributions from the community! Here’s how you can contribute:

### Pull Requests

- We appreciate pull requests that fix bugs, add features, or improve documentation.
- Please ensure your PR:
  - Is based on the latest `main` branch.
  - Includes clear descriptions and testing instructions.
  - Passes all automated tests and checks.

Once submitted, maintainers will review your PR and provide feedback or merge it if it meets the project standards.

### Issues

- Feel free to open issues for bugs, feature requests, or questions.
- When submitting an issue, please include:
  - A clear and descriptive title.
  - Steps to reproduce (for bugs).
  - Expected and actual behavior.
  - Any relevant environment or version information.

Maintainers will acknowledge your issue, label it appropriately, and work on resolving it or discuss it with you.

---

Thank you for helping improve this project! Your contributions make a difference.


## Thank you everyone's support :)
[![Star History Chart](https://star-history.dera.page/svg?repos=JasonHonKL/spy-search&type=Date)](https://star-history.dera.page/#JasonHonKL/spy-search&Date)
