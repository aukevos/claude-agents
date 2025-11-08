#!/usr/bin/env python3
"""
Research Agent - A CLI tool for automated web research and information gathering.
"""

import argparse
import json
import sys
from typing import List, Dict, Optional
from urllib.parse import quote_plus, urljoin
import requests
from bs4 import BeautifulSoup
import html2text
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()


class WebSearcher:
    """Handles web search operations using DuckDuckGo."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search DuckDuckGo for the given query.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of dictionaries containing 'title', 'url', and 'snippet'
        """
        try:
            # DuckDuckGo HTML search
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')
            results = []

            # Parse search results
            for result in soup.find_all('div', class_='result')[:max_results]:
                title_tag = result.find('a', class_='result__a')
                snippet_tag = result.find('a', class_='result__snippet')

                if title_tag:
                    title = title_tag.get_text(strip=True)
                    url = title_tag.get('href', '')
                    snippet = snippet_tag.get_text(strip=True) if snippet_tag else ''

                    # Extract actual URL from DuckDuckGo redirect
                    if url.startswith('//duckduckgo.com/l/?'):
                        # The actual URL is in the uddg parameter
                        try:
                            from urllib.parse import parse_qs, urlparse
                            parsed = urlparse(url)
                            actual_url = parse_qs(parsed.query).get('uddg', [''])[0]
                            if actual_url:
                                url = actual_url
                        except:
                            pass

                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet
                    })

            return results

        except Exception as e:
            console.print(f"[red]Error searching: {e}[/red]")
            return []


class ContentExtractor:
    """Handles fetching and extracting content from URLs."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = True
        self.html_converter.body_width = 0  # Don't wrap text

    def fetch_content(self, url: str) -> Optional[Dict[str, str]]:
        """
        Fetch and extract content from a URL.

        Args:
            url: URL to fetch

        Returns:
            Dictionary containing 'title', 'url', 'content' (markdown), and 'text' (plain)
        """
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'lxml')

            # Extract title
            title = ''
            if soup.title:
                title = soup.title.string.strip() if soup.title.string else ''
            elif soup.find('h1'):
                title = soup.find('h1').get_text(strip=True)

            # Remove script and style elements
            for script in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                script.decompose()

            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')

            if main_content:
                # Convert to markdown
                markdown_content = self.html_converter.handle(str(main_content))
                # Get plain text
                plain_text = main_content.get_text(separator='\n', strip=True)

                return {
                    'title': title,
                    'url': url,
                    'content': markdown_content,
                    'text': plain_text
                }

            return None

        except Exception as e:
            console.print(f"[yellow]Warning: Could not fetch {url}: {e}[/yellow]")
            return None


class ResearchAgent:
    """Main research agent orchestrator."""

    def __init__(self, verbose: bool = False):
        self.searcher = WebSearcher()
        self.extractor = ContentExtractor()
        self.verbose = verbose

    def research_topic(self, query: str, max_results: int = 5) -> Dict:
        """
        Research a topic by searching and extracting content.

        Args:
            query: Research query
            max_results: Maximum number of results to process

        Returns:
            Dictionary containing query, search results, and extracted content
        """
        if self.verbose:
            console.print(f"[cyan]Researching:[/cyan] {query}")

        # Search for results
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(description="Searching the web...", total=None)
            search_results = self.searcher.search(query, max_results)

        if not search_results:
            console.print("[red]No search results found.[/red]")
            return {'query': query, 'results': []}

        console.print(f"[green]Found {len(search_results)} results[/green]")

        # Extract content from each result
        extracted_content = []
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                description="Extracting content...",
                total=len(search_results)
            )

            for result in search_results:
                if self.verbose:
                    console.print(f"  Fetching: {result['url']}")

                content = self.extractor.fetch_content(result['url'])
                if content:
                    extracted_content.append({
                        **result,
                        'extracted': content
                    })

                progress.update(task, advance=1)

        console.print(f"[green]Successfully extracted {len(extracted_content)} articles[/green]")

        return {
            'query': query,
            'results': extracted_content
        }

    def research_url(self, url: str) -> Optional[Dict]:
        """
        Extract content from a specific URL.

        Args:
            url: URL to research

        Returns:
            Dictionary containing extracted content
        """
        if self.verbose:
            console.print(f"[cyan]Fetching:[/cyan] {url}")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            progress.add_task(description="Extracting content...", total=None)
            content = self.extractor.fetch_content(url)

        if content:
            console.print("[green]Content extracted successfully[/green]")
            return content
        else:
            console.print("[red]Failed to extract content[/red]")
            return None


class ResultFormatter:
    """Formats research results for output."""

    @staticmethod
    def format_markdown(data: Dict) -> str:
        """Format results as Markdown."""
        if 'query' in data:
            # Topic research format
            output = [f"# Research: {data['query']}\n"]
            output.append(f"*Generated by Research Agent*\n")
            output.append(f"*Found {len(data['results'])} results*\n")
            output.append("---\n")

            for i, result in enumerate(data['results'], 1):
                output.append(f"## {i}. {result['title']}\n")
                output.append(f"**URL:** {result['url']}\n")
                output.append(f"**Summary:** {result['snippet']}\n")

                if 'extracted' in result:
                    output.append("\n### Content\n")
                    # Truncate if too long
                    content = result['extracted']['content']
                    if len(content) > 5000:
                        content = content[:5000] + "\n\n*[Content truncated...]*"
                    output.append(content)

                output.append("\n---\n")

            return '\n'.join(output)
        else:
            # Single URL format
            output = [f"# {data['title']}\n"]
            output.append(f"**URL:** {data['url']}\n")
            output.append("\n---\n")
            output.append(data['content'])
            return '\n'.join(output)

    @staticmethod
    def format_json(data: Dict) -> str:
        """Format results as JSON."""
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def format_text(data: Dict) -> str:
        """Format results as plain text."""
        if 'query' in data:
            output = [f"Research: {data['query']}\n"]
            output.append(f"Found {len(data['results'])} results\n")
            output.append("="*80 + "\n")

            for i, result in enumerate(data['results'], 1):
                output.append(f"\n{i}. {result['title']}\n")
                output.append(f"URL: {result['url']}\n")
                output.append(f"Summary: {result['snippet']}\n")

                if 'extracted' in result:
                    output.append("\nContent:\n")
                    text = result['extracted']['text']
                    if len(text) > 3000:
                        text = text[:3000] + "\n[Content truncated...]"
                    output.append(text)

                output.append("\n" + "-"*80 + "\n")

            return '\n'.join(output)
        else:
            output = [f"{data['title']}\n"]
            output.append(f"URL: {data['url']}\n")
            output.append("="*80 + "\n")
            output.append(data['text'])
            return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Research Agent - Automated web research and information gathering',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        'query',
        nargs='?',
        help='Research topic or question'
    )
    parser.add_argument(
        '--url',
        help='Fetch content from a specific URL instead of searching'
    )
    parser.add_argument(
        '-o', '--output',
        help='Save results to a file'
    )
    parser.add_argument(
        '--format',
        choices=['markdown', 'json', 'text'],
        default='markdown',
        help='Output format (default: markdown)'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=5,
        help='Maximum number of search results to process (default: 5)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress information'
    )

    args = parser.parse_args()

    # Validate input
    if not args.query and not args.url:
        parser.error('Either a query or --url must be provided')

    if args.query and args.url:
        parser.error('Cannot specify both query and --url')

    # Initialize agent
    agent = ResearchAgent(verbose=args.verbose)
    formatter = ResultFormatter()

    # Perform research
    try:
        if args.url:
            # Research specific URL
            result = agent.research_url(args.url)
            if not result:
                sys.exit(1)
        else:
            # Research topic
            result = agent.research_topic(args.query, args.max_results)
            if not result.get('results'):
                sys.exit(1)

        # Format output
        if args.format == 'markdown':
            output = formatter.format_markdown(result)
        elif args.format == 'json':
            output = formatter.format_json(result)
        else:
            output = formatter.format_text(result)

        # Save or print
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
            console.print(f"[green]Results saved to {args.output}[/green]")
        else:
            if args.format == 'markdown':
                console.print(Markdown(output))
            else:
                console.print(output)

    except KeyboardInterrupt:
        console.print("\n[yellow]Research interrupted by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
