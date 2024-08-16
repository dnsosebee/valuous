import subprocess


def get_porcelain_status():
    return subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout


def commit_all(message="Auto-commit"):
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', message])


def fetch_branch(branch_name='user'):
    subprocess.run(['git', 'fetch', 'origin', branch_name])


def merge(branch_name='user'):
    return subprocess.run(['git', 'merge', f'origin/{branch_name}'])


def abort_merge():
    return subprocess.run(['git', 'merge', '--abort'])


def push():
    subprocess.run(['git', 'push'])
