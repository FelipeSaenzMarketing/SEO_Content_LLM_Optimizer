# 📚 Content Analyzer for LLM Citability

A Streamlit-based web application that analyzes written content to determine how effectively it can be cited and referenced by Large Language Models (LLMs).

## 🎯 Features

- **Comprehensive Text Analysis**: Word count, sentence structure, paragraph organization
- **LLM-Optimized Metrics**: Heading ratios, list usage, structural elements
- **Citability Signals**: Numbers, URLs, citation-like patterns
- **Lexical Diversity**: Type-token ratio calculations
- **Repetition Detection**: Bigram analysis
- **Dual Input Modes**: Paste text or crawl URLs
- **Actionable Recommendations**: Specific suggestions to improve content

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/content-analyzer-llm.git
cd content-analyzer-llm

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## 📋 Usage

### Option 1: Analyze Pasted Content
1. Paste your content into the text area
2. Click "Analyze pasted content"
3. Review metrics and recommendations

### Option 2: Analyze a URL
1. Enter a URL
2. Click "Crawl URL and analyze"
3. Review extracted content and analysis

## 📊 Metrics Explained

- **Word/Sentence/Paragraph Count**: Basic text statistics
- **Average Sentence Length**: Target ≤ 25 words
- **Heading Ratio**: Target ≥ 0.20
- **List Ratio**: Target ≥ 0.10
- **Numbers/URLs/Citations**: Citability signals
- **Type-Token Ratio**: Lexical diversity
- **Repetition Score**: Content redundancy

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📝 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

Built with [Streamlit](https://streamlit.io/), [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)

---

Made with ❤️ for better content optimization
