# Spy Search

**Spy Search** is an agentic search framework designed to outperform current web search agents with a focus on faster, more efficient daily usage.

While commercial solutions like Manus charge $200 per month, Spy Search leverages open-source models to provide a cost-effective alternative without sacrificing performance.
Currently our searching-speed is quite slow yet we can generate a long length consistent report (around 2000 words) with latest current infomration! This problem will be tackle after the release of v1.0. 

---

## Roadmap
**News**: Spy-searcher has just released v0.3 ! 

- **Version 1.0:** Agentic Search Functionality  
- **Version 2.0:** Localized Cache to Accelerate Search Speed  

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

Add your API key in the .env file if you want to use API. Currently we support openAI, Claude, Gork & Deepseek. If you use ollama you don't need to do anything. 

config the config.json file, you may copy the following template
```json
{
    "provider": "ollama",
    "model": "deepseek-r1:7b",
    "agents": [
        "reporter"
    ]
}
```

After that run 
```shell
docker build -t spy-searcher .   
docker run -p 8000:8000 -p 8080:8080 spy-searcher
```

Now you can access  
[http://localhost:8000](http://localhost:8000)


## Community 
[Discord](https://discord.gg/rrsMgBdJJt)


## Example 

- [Example Report (HTML)](./docs/examples/example_report.html)

![Example Search](./docs/examples/example_search.png)

## Demo Video

Watch the demo video on YouTube:

[![Demo Video](https://img.youtube.com/vi/Dgb33BHtRwQ/0.jpg)](https://youtu.be/Dgb33BHtRwQ)

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
[![Star History Chart](https://api.star-history.com/svg?repos=JasonHonKL/spy-search&type=Date)](https://star-history.com/#JasonHonKL/spy-search&Date)
