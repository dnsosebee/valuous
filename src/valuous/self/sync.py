from valuous.peripherals import git
from valuous.peripherals.memory import remember
from valuous.self.decorators import trace

USER_BRANCH = "user"


@trace("keep up with user branch")
def sync_git():
    status = git.get_porcelain_status()
    if status:
        remember("Committing local changes.")
        git.commit_all()
    git.fetch_branch(USER_BRANCH)
    git.merge(USER_BRANCH)
    status = git.get_porcelain_status()
    if 'UU' in status:
        remember("Merge conflict detected. Aborting merge.")
        git.abort_merge()
    git.push()

# test
