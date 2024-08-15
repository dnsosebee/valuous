import subprocess

from valuous.self.procedure import procedure


def check_git_status():
    return subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout


def commit_changes(message="Auto-commit"):
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', message])


def fetch_user_branch(branch_name='user'):
    subprocess.run(['git', 'fetch', 'origin', branch_name])


def check_and_merge(branch_name='user'):
    result = subprocess.run(['git', 'merge-tree', 'HEAD',
                            'origin/' + branch_name], capture_output=True, text=True)
    if "<<<<<<< ours" not in result.stdout:
        subprocess.run(['git', 'merge', 'origin/' + branch_name])
        return True
    return False


def push_changes():
    subprocess.run(['git', 'push'])


@procedure
def git_process():
    if check_git_status():
        commit_changes()
    fetch_user_branch()
    if check_and_merge():
        push_changes()
    else:
        print("Conflicts detected. Manual resolution needed.")

# Adding a comment
