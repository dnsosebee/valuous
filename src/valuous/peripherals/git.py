import subprocess


def get_porcelain_status():
    return subprocess.run(['git', 'status', '--porcelain'], text=True, stdout=subprocess.PIPE).stdout


def commit_all(message="Auto-commit"):
    subprocess.run(['git', 'add', '.'], stdout=subprocess.DEVNULL)
    subprocess.run(['git', 'commit', '-m', message], stdout=subprocess.DEVNULL)


def fetch_branch(branch_name='user'):
    subprocess.run(['git', 'fetch', 'origin', branch_name],
                   stdout=subprocess.DEVNULL)


def merge(branch_name='user'):
    return subprocess.run(['git', 'merge', f'origin/{branch_name}'], stdout=subprocess.DEVNULL)


def abort_merge():
    return subprocess.run(['git', 'merge', '--abort'], stdout=subprocess.DEVNULL)


def push():
    subprocess.run(['git', 'push'], stdout=subprocess.DEVNULL)
