import os
import sys
import shutil
from pathlib import Path
from dulwich.repo import Repo
from dulwich.porcelain import init, add, commit, push

repo_dir = Path(__file__).resolve().parent.parent

# Clean .git
git_dir = repo_dir / ".git"
if git_dir.exists():
    shutil.rmtree(str(git_dir), ignore_errors=True)

# Remove push script from index
repo = init(str(repo_dir))
add(str(repo_dir))

c_sha = commit(
    str(repo_dir),
    message=b"feat: complete Delhi NCR Airbnb analytics platform with INR (Rs) currency and bundled datasets",
    author=b"Data Analyst <analyst@example.com>",
    committer=b"Data Analyst <analyst@example.com>",
)
print("Committed successfully.")

token = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GITHUB_TOKEN", "")
remote_url = f"https://ayushsammu123-dotcom:{token}@github.com/ayushsammu123-dotcom/airbnb.git"

push(str(repo_dir), remote_url, refspecs=[b"+refs/heads/master:refs/heads/main"])
print(">> PUSHED TO GITHUB (MAIN BRANCH)!")
