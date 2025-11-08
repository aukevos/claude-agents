# Claude Agents

A collection of Python-based CLI automation agents for research, GitHub operations, and productivity.

## Agents

### 1. Research Agent
Automated web research and information gathering tool.

**Features:**
- Web search using DuckDuckGo
- URL content extraction
- Multiple output formats (Markdown, JSON, plain text)
- Smart content filtering

### 2. GitHub Agent
Automate GitHub and git operations with ease.

**Features:**
- Git operations (status, push, pull, commit)
- GitHub operations (create repos, issues, PRs)
- Credential management
- Quick sync commands

## Installation

```bash
# Clone the repository
git clone https://github.com/aukevos/claude-agents.git
cd claude-agents

# Install dependencies
pip install -r requirements.txt

# Install globally (optional)
cp research_agent.py ~/.local/bin/research-agent
cp github_agent.py ~/.local/bin/github-agent
chmod +x ~/.local/bin/research-agent ~/.local/bin/github-agent

# Make sure ~/.local/bin is in your PATH
export PATH="$HOME/.local/bin:$PATH"
```

## Usage

---

## Research Agent

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

---

## GitHub Agent

A powerful CLI tool for automating GitHub and git operations based on real-world credential handling.

### Commands

#### Git Operations

**Status**
```bash
github-agent status              # Show git status
github-agent status -v           # Show detailed status with recent commits
```

**Pull**
```bash
github-agent pull                # Pull from current branch
github-agent pull --branch dev   # Pull from specific branch
```

**Push**
```bash
github-agent push                # Push to current branch
github-agent push --force        # Force push (use with caution)
```

**Commit**
```bash
github-agent commit "Fix bug"              # Commit staged changes
github-agent commit "Add feature" --all    # Stage and commit all changes
```

**Sync**
```bash
github-agent sync                          # Pull, commit all, and push
github-agent sync --message "Update docs"  # Sync with custom message
```

#### GitHub Operations

**Create Repository**
```bash
github-agent create-repo my-project --description "My awesome project"
github-agent create-repo my-app --private --push    # Private repo with initial push
```

**Issues**
```bash
github-agent create-issue "Bug in login" --body "Steps to reproduce..." --labels bug urgent
github-agent list-issues                   # List open issues
github-agent list-issues --state closed    # List closed issues
github-agent list-issues --limit 20        # Show more issues
```

**Pull Requests**
```bash
github-agent create-pr "Add new feature" --body "Description..." --base main
github-agent list-prs                      # List open PRs
github-agent list-prs --state merged       # List merged PRs
```

#### Utilities

**Check Authentication**
```bash
github-agent check-auth          # Verify GitHub CLI authentication
```

**Fix Credentials**
```bash
github-agent fix-creds           # Fix git credential issues
```

This command automatically:
- Reads your `gh` CLI token
- Updates `~/.git-credentials`
- Updates the current repo's remote URL
- Fixes authentication errors

### Examples

**Quick workflow:**
```bash
# Start your day
github-agent pull

# Work on code...

# Commit and push
github-agent commit "Implement feature X" --all
github-agent push

# Create a PR
github-agent create-pr "Feature X implementation" --body "Adds feature X with tests"
```

**Initialize new project:**
```bash
# Create local repo and push to GitHub
git init
# Add your code
github-agent create-repo my-awesome-project --description "An awesome project" --push
```

**Fix authentication issues:**
```bash
# If you get 403 or credential errors
github-agent fix-creds
github-agent push
```

---

## Future Enhancements

### Research Agent
- [ ] LLM integration for intelligent summarization
- [ ] Multi-source aggregation (academic papers, news, forums)
- [ ] Interactive mode for iterative research
- [ ] Citation tracking and source credibility scoring
- [ ] Research history and caching

### GitHub Agent
- [ ] Branch management (create, delete, switch)
- [ ] Release management
- [ ] GitHub Actions workflow triggers
- [ ] Collaborative features (assign issues, review PRs)
- [ ] Repository insights and statistics

## License

MIT
