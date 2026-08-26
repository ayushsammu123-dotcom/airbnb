"""
Pure Python Git repository initializer and commit tool using Dulwich.
"""
from pathlib import Path
from dulwich.repo import Repo
from dulwich.porcelain import init, add, commit, status

repo_dir = Path(__file__).resolve().parent.parent

print(f">> Initializing Git repository in: {repo_dir}")

# Check if .git already exists
git_dir = repo_dir / ".git"
if not git_dir.exists():
    repo = init(str(repo_dir))
    print(">> Initialized new Git repository.")
else:
    repo = Repo(str(repo_dir))
    print(">> Found existing Git repository.")

# Stage all files
print(">> Staging files...")
add(str(repo_dir))

# Commit
try:
    commit_sha = commit(
        str(repo_dir),
        message=b"feat: Airbnb Pricing & Revenue Analytics Platform (Delhi NCR Edition)",
        author=b"Data Analyst <analyst@example.com>",
        committer=b"Data Analyst <analyst@example.com>",
    )
    print(f">> Successfully committed: {commit_sha.decode('utf-8')}")
except Exception as e:
    print(f">> Commit note: {e}")

st = status(str(repo_dir))
print(f">> Staged: {len(st.staged['add'])} files | Untracked: {len(st.untracked)} files")
