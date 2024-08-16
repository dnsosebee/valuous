from valuous.peripherals.git import (commit_all, fetch_branch,
                                     get_porcelain_status, merge)

USER_BRANCH = "user"


def sync_git():
    status = get_porcelain_status()
    if status:
        commit_all()
    fetch_branch(USER_BRANCH)
    merge(USER_BRANCH)
    status = get_porcelain_status()
    # check for conflicts
