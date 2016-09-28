import requests
import sublime
import os
import subprocess
from subprocess import CalledProcessError
from .utils import find_git
from .utils import log
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


class LoadRepoList:

    def __init__(self):
        self.username = None
        self.repo_name = None
        self.window = sublime.active_window()
        self.entries = None

    def format_entries(self):
        repo_list = []
        folder_list = sublime.active_window().folders()
        if folder_list:
            for folder_path in folder_list:
                repo_info = get_github_repo_info(folder_path)
                if repo_info != (-1, -1):
                    repo_list.append(repo_info)
        entries = ["manually enter repository..."]
        entries.extend(["{}/{}".format(repo[0], repo[1]) for repo in repo_list])
        self.entries = entries
        print(self.entries)

    def show_selection_panel(self):
        self.window.show_quick_panel(self.entries, self.on_repo_selection)

    def on_done(self, content):
        if '/' in content:
            self.username, self.repo_name = content.split('/')
            print(self.username + '/' + self.repo_name)
        else:
            raise Exception("Please enter repo in the format username/repo_name")

    def on_repo_selection(self, selection):
        if selection >= 0:
            if selection == 0:
                self.window.run_command('hide_panel')
                self.window.show_input_panel('Enter repo in the format username/repo_name:', '', self.on_done, None, None)
            else:
                print(selection)
                print(self.entries[selection])
                self.username, self.repo_name = self.entries[selection].split('/')


def get_github_repo_info(folder_path):
    '''
    Find the repo name. It essentially does two attempts:
    - First it try the open folder's name
    - If the first attempt fails, it tries to run "git config --get remote.origin.url" in current directory
    '''
    git = find_git()
    cmd = [git, '-C', folder_path, 'config', '--get', 'remote.origin.url']
    try:
        try:
            repo_url = subprocess.check_output(' '.join(cmd), shell=True)
        except CalledProcessError:
            return (-1, -1)
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
