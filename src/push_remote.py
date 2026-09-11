"""
Push committed local repository to remote GitHub repository using Dulwich.

Usage:
    python src/push_remote.py <GITHUB_REPO_URL> [GITHUB_TOKEN]
"""
import sys
from pathlib import Path
from dulwich.porcelain import push

repo_dir = Path(__file__).resolve().parent.parent

if len(sys.argv) < 2:
    print("Usage: python src/push_remote.py <REMOTE_URL> [TOKEN]")
    sys.exit(1)

remote_url = sys.argv[1]
token = sys.argv[2] if len(sys.argv) > 2 else None

if token and "https://" in remote_url and "@" not in remote_url:
    # Insert token for auth
    remote_url = remote_url.replace("https://", f"https://oauth2:{token}@")

print(f">> Pushing to {sys.argv[1]}...")
try:
    push(str(repo_dir), remote_url, refspecs=[b"refs/heads/master:refs/heads/main"])
    print(">> Successfully pushed to GitHub!")
except Exception as e:
    # Try pushing master to master
    try:
        push(str(repo_dir), remote_url, refspecs=[b"refs/heads/master:refs/heads/master"])
        print(">> Successfully pushed to GitHub (branch: master)!")
    except Exception as e2:
        print(f">> Push error: {e2}")
        print(">> Note: If authenticating over HTTPS, provide your GitHub Personal Access Token.")
