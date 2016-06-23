import requests
import sublime
import os
import subprocess
from .utils import find_git
import re


class GitHubAccount:
    def __init__(self, settings):
        self.session = requests.Session()
        self.settings = settings
        api_token = self.settings.get('token', '')
        self.username = self.settings.get('username', '')
        password = self.settings.get('password', '')
        if api_token:
            self.session.headers['Authorization'] = 'token %s' % api_token
        elif self.username and password:
            self.session.auth = (self.username, password)
        else:
            raise Exception("Please check the authentication settings!")
        self.session.headers['content-type'] = 'application/json'

    def join_issue_url(self, username=None, repo_name=None, issue_number=None):
        API_URL = 'https://api.github.com/repos'
        if not username:
            username = self.username
        if repo_name:
            if not issue_number:
                return '/'.join([API_URL, username, repo_name, 'issues'])
            else:
                return '/'.join([API_URL, username, repo_name, 'issues', issue_number])
        else:
            raise Exception("Please check whether the repo_name is correct.")


def get_github_repo_info():
    '''
    Find the repo name. It essentially does two attempts:
    - First it try the open folder's name
    - If the first attempt fails, it tries to run "git config --get remote.origin.url" in current directory
    '''
    current_window = sublime.active_window()
    file_name = current_window.active_view().file_name()
    try:
        folder = os.path.abspath(os.path.dirname(file_name))
    except:
        folder = current_window.folders()[0]
    git = find_git()
    cmd = [git, '-C', folder, 'config', '--get', 'remote.origin.url']
    try:
        repo_url = subprocess.check_output(' '.join(cmd), shell=True)
        repo_url = repo_url.decode('utf-8')
        if repo_url.startswith('https'):
            repo_url = re.search(r'(?<=https://github.com/).*', repo_url).group(0)
        elif repo_url.startswith('git'):
            repo_url = re.search(r'(?<=git@github.com:).*', repo_url).group(0)
        else:
            raise Exception('repo URL error!')
        username, raw_repo_name = os.path.split(repo_url)
        raw_repo_name = raw_repo_name.replace("\n", "")
        repo_name = raw_repo_name.replace("\r", "")
    except:
        raise Exception("Error in find repo URL!")
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    return (username, repo_name)
