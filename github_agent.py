#!/usr/bin/env python3
"""
GitHub Agent - A CLI tool for automating GitHub and git operations.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

console = Console()


class GitOperations:
    """Handles git operations."""

    @staticmethod
    def run_git_command(args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a git command and return the result."""
        try:
            result = subprocess.run(
                ['git'] + args,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except Exception as e:
            console.print(f"[red]Error running git command: {e}[/red]")
            sys.exit(1)

    @staticmethod
    def is_git_repo() -> bool:
        """Check if current directory is a git repository."""
        result = GitOperations.run_git_command(['rev-parse', '--git-dir'])
        return result.returncode == 0

    @staticmethod
    def get_current_branch() -> Optional[str]:
        """Get the current git branch name."""
        result = GitOperations.run_git_command(['branch', '--show-current'])
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    @staticmethod
    def get_remote_url() -> Optional[str]:
        """Get the remote URL for origin."""
        result = GitOperations.run_git_command(['remote', 'get-url', 'origin'])
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    @staticmethod
    def has_uncommitted_changes() -> bool:
        """Check if there are uncommitted changes."""
        result = GitOperations.run_git_command(['status', '--porcelain'])
        return bool(result.stdout.strip())

    @staticmethod
    def status(verbose: bool = False):
        """Show git status."""
        if not GitOperations.is_git_repo():
            console.print("[red]Not a git repository[/red]")
            return False

        console.print("\n[cyan]Git Status[/cyan]")

        # Branch info
        branch = GitOperations.get_current_branch()
        console.print(f"Branch: [green]{branch}[/green]")

        # Remote info
        remote = GitOperations.get_remote_url()
        if remote:
            console.print(f"Remote: [blue]{remote}[/blue]")

        # Status
        result = GitOperations.run_git_command(['status', '--short'])
        if result.stdout:
            console.print("\n[yellow]Changes:[/yellow]")
            console.print(result.stdout)
        else:
            console.print("\n[green]Working tree clean[/green]")

        if verbose:
            # Show recent commits
            console.print("\n[cyan]Recent commits:[/cyan]")
            GitOperations.run_git_command(['log', '--oneline', '-5'], capture_output=False)

        return True

    @staticmethod
    def pull(branch: Optional[str] = None):
        """Pull latest changes from remote."""
        if not GitOperations.is_git_repo():
            console.print("[red]Not a git repository[/red]")
            return False

        current_branch = branch or GitOperations.get_current_branch()

        console.print(f"[cyan]Pulling from origin/{current_branch}...[/cyan]")
        result = GitOperations.run_git_command(['pull', 'origin', current_branch], capture_output=False)

        if result.returncode == 0:
            console.print("[green]Pull successful[/green]")
            return True
        else:
            console.print("[red]Pull failed[/red]")
            return False

    @staticmethod
    def push(branch: Optional[str] = None, force: bool = False):
        """Push changes to remote."""
        if not GitOperations.is_git_repo():
            console.print("[red]Not a git repository[/red]")
            return False

        current_branch = branch or GitOperations.get_current_branch()

        args = ['push', 'origin', current_branch]
        if force:
            console.print("[yellow]Warning: Force pushing...[/yellow]")
            args.append('--force')

        console.print(f"[cyan]Pushing to origin/{current_branch}...[/cyan]")
        result = GitOperations.run_git_command(args, capture_output=False)

        if result.returncode == 0:
            console.print("[green]Push successful[/green]")
            return True
        else:
            console.print("[red]Push failed[/red]")
            console.print("[yellow]Tip: Run 'github-agent fix-creds' if you have authentication issues[/yellow]")
            return False

    @staticmethod
    def commit(message: str, add_all: bool = False):
        """Commit changes."""
        if not GitOperations.is_git_repo():
            console.print("[red]Not a git repository[/red]")
            return False

        if add_all:
            console.print("[cyan]Staging all changes...[/cyan]")
            GitOperations.run_git_command(['add', '.'])

        if not GitOperations.has_uncommitted_changes():
            console.print("[yellow]No changes to commit[/yellow]")
            return False

        console.print("[cyan]Creating commit...[/cyan]")
        result = GitOperations.run_git_command(['commit', '-m', message], capture_output=False)

        if result.returncode == 0:
            console.print("[green]Commit successful[/green]")
            return True
        else:
            console.print("[red]Commit failed[/red]")
            return False


class GitHubOperations:
    """Handles GitHub operations using gh CLI."""

    @staticmethod
    def run_gh_command(args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run a gh CLI command and return the result."""
        try:
            result = subprocess.run(
                ['gh'] + args,
                capture_output=capture_output,
                text=True,
                check=False
            )
            return result
        except FileNotFoundError:
            console.print("[red]Error: gh CLI not found. Please install it first.[/red]")
            console.print("Visit: https://cli.github.com/")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error running gh command: {e}[/red]")
            sys.exit(1)

    @staticmethod
    def check_auth() -> bool:
        """Check if user is authenticated with GitHub."""
        result = GitHubOperations.run_gh_command(['auth', 'status'])
        return result.returncode == 0

    @staticmethod
    def get_auth_user() -> Optional[str]:
        """Get the authenticated GitHub username."""
        result = GitHubOperations.run_gh_command(['api', 'user', '--jq', '.login'])
        if result.returncode == 0:
            return result.stdout.strip()
        return None

    @staticmethod
    def create_repo(name: str, description: str = "", public: bool = True, push: bool = False):
        """Create a new GitHub repository."""
        if not GitOperations.is_git_repo():
            console.print("[yellow]Not a git repository. Initializing...[/yellow]")
            GitOperations.run_git_command(['init'])

        visibility = '--public' if public else '--private'
        args = ['repo', 'create', name, visibility, '--source', '.']

        if description:
            args.extend(['--description', description])

        if push:
            args.append('--push')

        console.print(f"[cyan]Creating repository: {name}...[/cyan]")
        result = GitHubOperations.run_gh_command(args, capture_output=False)

        if result.returncode == 0:
            console.print(f"[green]Repository created successfully[/green]")
            user = GitHubOperations.get_auth_user()
            console.print(f"[blue]https://github.com/{user}/{name}[/blue]")
            return True
        else:
            console.print("[red]Failed to create repository[/red]")
            return False

    @staticmethod
    def create_issue(title: str, body: str = "", labels: List[str] = None):
        """Create a GitHub issue."""
        args = ['issue', 'create', '--title', title]

        if body:
            args.extend(['--body', body])

        if labels:
            args.extend(['--label', ','.join(labels)])

        console.print("[cyan]Creating issue...[/cyan]")
        result = GitHubOperations.run_gh_command(args, capture_output=False)

        if result.returncode == 0:
            console.print("[green]Issue created successfully[/green]")
            return True
        else:
            console.print("[red]Failed to create issue[/red]")
            return False

    @staticmethod
    def list_issues(state: str = "open", limit: int = 10):
        """List GitHub issues."""
        args = ['issue', 'list', '--state', state, '--limit', str(limit), '--json',
                'number,title,state,labels,createdAt']

        result = GitHubOperations.run_gh_command(args)

        if result.returncode != 0:
            console.print("[red]Failed to fetch issues[/red]")
            return False

        try:
            issues = json.loads(result.stdout)

            if not issues:
                console.print(f"[yellow]No {state} issues found[/yellow]")
                return True

            table = Table(title=f"{state.capitalize()} Issues")
            table.add_column("#", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Labels", style="yellow")
            table.add_column("Created", style="green")

            for issue in issues:
                labels = ', '.join([l['name'] for l in issue.get('labels', [])])
                created = issue.get('createdAt', '').split('T')[0]
                table.add_row(
                    str(issue['number']),
                    issue['title'],
                    labels,
                    created
                )

            console.print(table)
            return True

        except json.JSONDecodeError:
            console.print("[red]Failed to parse issues[/red]")
            return False

    @staticmethod
    def create_pr(title: str, body: str = "", base: str = "main"):
        """Create a pull request."""
        args = ['pr', 'create', '--title', title, '--base', base]

        if body:
            args.extend(['--body', body])

        console.print("[cyan]Creating pull request...[/cyan]")
        result = GitHubOperations.run_gh_command(args, capture_output=False)

        if result.returncode == 0:
            console.print("[green]Pull request created successfully[/green]")
            return True
        else:
            console.print("[red]Failed to create pull request[/red]")
            return False

    @staticmethod
    def list_prs(state: str = "open", limit: int = 10):
        """List pull requests."""
        args = ['pr', 'list', '--state', state, '--limit', str(limit), '--json',
                'number,title,state,headRefName,createdAt']

        result = GitHubOperations.run_gh_command(args)

        if result.returncode != 0:
            console.print("[red]Failed to fetch pull requests[/red]")
            return False

        try:
            prs = json.loads(result.stdout)

            if not prs:
                console.print(f"[yellow]No {state} pull requests found[/yellow]")
                return True

            table = Table(title=f"{state.capitalize()} Pull Requests")
            table.add_column("#", style="cyan")
            table.add_column("Title", style="white")
            table.add_column("Branch", style="yellow")
            table.add_column("Created", style="green")

            for pr in prs:
                created = pr.get('createdAt', '').split('T')[0]
                table.add_row(
                    str(pr['number']),
                    pr['title'],
                    pr['headRefName'],
                    created
                )

            console.print(table)
            return True

        except json.JSONDecodeError:
            console.print("[red]Failed to parse pull requests[/red]")
            return False


class CredentialManager:
    """Handles git credential management."""

    @staticmethod
    def get_gh_token() -> Optional[str]:
        """Get the gh CLI OAuth token."""
        try:
            # Try to find gh config
            gh_config_paths = [
                Path.home() / 'snap/gh/current/.config/gh/hosts.yml',
                Path.home() / 'snap/gh' / os.listdir(Path.home() / 'snap/gh')[0] / '.config/gh/hosts.yml'
                    if (Path.home() / 'snap/gh').exists() else None,
                Path.home() / '.config/gh/hosts.yml',
            ]

            for config_path in gh_config_paths:
                if config_path and config_path.exists():
                    with open(config_path, 'r') as f:
                        for line in f:
                            if 'oauth_token:' in line:
                                return line.split('oauth_token:')[1].strip()

            return None
        except Exception as e:
            console.print(f"[yellow]Could not read gh config: {e}[/yellow]")
            return None

    @staticmethod
    def fix_credentials():
        """Fix git credentials using gh CLI token."""
        console.print("[cyan]Checking authentication...[/cyan]")

        if not GitHubOperations.check_auth():
            console.print("[red]Not authenticated with GitHub CLI[/red]")
            console.print("Run: [yellow]gh auth login[/yellow]")
            return False

        user = GitHubOperations.get_auth_user()
        console.print(f"[green]Authenticated as: {user}[/green]")

        token = CredentialManager.get_gh_token()
        if not token:
            console.print("[red]Could not find gh CLI token[/red]")
            return False

        console.print(f"[cyan]Found token: {token[:8]}...[/cyan]")

        # Update git credentials file
        creds_file = Path.home() / '.git-credentials'
        creds_file.write_text(f"https://{user}:{token}@github.com\n")
        console.print(f"[green]Updated {creds_file}[/green]")

        # Update remote URL if in a git repo
        if GitOperations.is_git_repo():
            remote = GitOperations.get_remote_url()
            if remote and 'github.com' in remote:
                # Extract repo path
                repo_path = remote.split('github.com/')[-1].replace('.git', '')
                new_url = f"https://{user}:{token}@github.com/{repo_path}.git"

                GitOperations.run_git_command(['remote', 'set-url', 'origin', new_url])
                console.print(f"[green]Updated remote URL[/green]")

        console.print("[green]Credentials fixed successfully![/green]")
        return True


def main():
    parser = argparse.ArgumentParser(
        description='GitHub Agent - Automate GitHub and git operations',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Git operations
    status_parser = subparsers.add_parser('status', help='Show git status')
    status_parser.add_argument('-v', '--verbose', action='store_true', help='Show detailed status')

    pull_parser = subparsers.add_parser('pull', help='Pull from remote')
    pull_parser.add_argument('--branch', help='Branch to pull (default: current)')

    push_parser = subparsers.add_parser('push', help='Push to remote')
    push_parser.add_argument('--branch', help='Branch to push (default: current)')
    push_parser.add_argument('--force', action='store_true', help='Force push')

    commit_parser = subparsers.add_parser('commit', help='Commit changes')
    commit_parser.add_argument('message', help='Commit message')
    commit_parser.add_argument('-a', '--all', action='store_true', help='Stage all changes')

    # GitHub operations
    create_repo_parser = subparsers.add_parser('create-repo', help='Create GitHub repository')
    create_repo_parser.add_argument('name', help='Repository name')
    create_repo_parser.add_argument('--description', default='', help='Repository description')
    create_repo_parser.add_argument('--private', action='store_true', help='Make repository private')
    create_repo_parser.add_argument('--push', action='store_true', help='Push initial commit')

    create_issue_parser = subparsers.add_parser('create-issue', help='Create GitHub issue')
    create_issue_parser.add_argument('title', help='Issue title')
    create_issue_parser.add_argument('--body', default='', help='Issue body')
    create_issue_parser.add_argument('--labels', nargs='+', help='Issue labels')

    list_issues_parser = subparsers.add_parser('list-issues', help='List GitHub issues')
    list_issues_parser.add_argument('--state', choices=['open', 'closed', 'all'], default='open')
    list_issues_parser.add_argument('--limit', type=int, default=10, help='Max issues to show')

    create_pr_parser = subparsers.add_parser('create-pr', help='Create pull request')
    create_pr_parser.add_argument('title', help='PR title')
    create_pr_parser.add_argument('--body', default='', help='PR body')
    create_pr_parser.add_argument('--base', default='main', help='Base branch')

    list_prs_parser = subparsers.add_parser('list-prs', help='List pull requests')
    list_prs_parser.add_argument('--state', choices=['open', 'closed', 'merged', 'all'], default='open')
    list_prs_parser.add_argument('--limit', type=int, default=10, help='Max PRs to show')

    # Utilities
    subparsers.add_parser('check-auth', help='Check GitHub authentication')
    subparsers.add_parser('fix-creds', help='Fix git credentials')

    sync_parser = subparsers.add_parser('sync', help='Sync: pull, commit all, push')
    sync_parser.add_argument('--message', default='Sync changes', help='Commit message')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute commands
    try:
        if args.command == 'status':
            GitOperations.status(args.verbose)

        elif args.command == 'pull':
            GitOperations.pull(args.branch)

        elif args.command == 'push':
            GitOperations.push(args.branch, args.force)

        elif args.command == 'commit':
            GitOperations.commit(args.message, args.all)

        elif args.command == 'create-repo':
            GitHubOperations.create_repo(args.name, args.description, not args.private, args.push)

        elif args.command == 'create-issue':
            GitHubOperations.create_issue(args.title, args.body, args.labels)

        elif args.command == 'list-issues':
            GitHubOperations.list_issues(args.state, args.limit)

        elif args.command == 'create-pr':
            GitHubOperations.create_pr(args.title, args.body, args.base)

        elif args.command == 'list-prs':
            GitHubOperations.list_prs(args.state, args.limit)

        elif args.command == 'check-auth':
            if GitHubOperations.check_auth():
                user = GitHubOperations.get_auth_user()
                console.print(f"[green]Authenticated as: {user}[/green]")
            else:
                console.print("[red]Not authenticated[/red]")
                console.print("Run: [yellow]gh auth login[/yellow]")

        elif args.command == 'fix-creds':
            CredentialManager.fix_credentials()

        elif args.command == 'sync':
            console.print("[cyan]Syncing repository...[/cyan]")
            GitOperations.pull()
            if GitOperations.has_uncommitted_changes():
                GitOperations.commit(args.message, add_all=True)
            GitOperations.push()
            console.print("[green]Sync complete![/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
