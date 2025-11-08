# Research Agent

A Python-based CLI tool for automated web research and information gathering.

## Features

- **Web Search**: Search the web for relevant information on any topic
- **URL Fetching**: Fetch and parse content from specific URLs
- **Content Extraction**: Extract clean text from web pages
- **Multiple Output Formats**: Save results as Markdown, JSON, or plain text
- **Smart Filtering**: Remove clutter and focus on relevant content
- **Extensible**: Easy to add new data sources and features

## Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd personalprojects

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Research
```bash
python research_agent.py "artificial intelligence trends 2025"
```

### Search and Save Results
```bash
python research_agent.py "Python best practices" --output report.md
```

### Fetch Specific URLs
```bash
python research_agent.py --url https://example.com/article --output article.md
```

### Advanced Options
```bash
# Export as JSON
python research_agent.py "machine learning" --format json --output results.json

# Verbose output
python research_agent.py "web scraping" --verbose
```

## Options

- `query`: Research topic or question (positional argument)
- `--url`: Fetch content from a specific URL instead of searching
- `--output, -o`: Save results to a file
- `--format`: Output format (markdown, json, text) - default: markdown
- `--max-results`: Maximum number of search results to process - default: 5
- `--verbose, -v`: Show detailed progress information

## Examples

1. **Quick research on a topic:**
   ```bash
   python research_agent.py "best practices for REST APIs"
   ```

2. **Deep dive with more results:**
   ```bash
   python research_agent.py "GraphQL vs REST" --max-results 10 --output comparison.md
   ```

3. **Fetch and analyze a specific article:**
   ```bash
   python research_agent.py --url https://blog.example.com/article --format markdown
   ```

## Future Enhancements

- [ ] LLM integration for intelligent summarization
- [ ] Multi-source aggregation (academic papers, news, forums)
- [ ] Interactive mode for iterative research
- [ ] Citation tracking and source credibility scoring
- [ ] Research history and caching

## License

MIT
