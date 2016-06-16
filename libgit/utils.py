import sublime
from . import github.GitHub
import os
import subprocess

SETTINGS = sublime.load_settings('github_issue.sublime-settings')


class Account:
    def __init__(self, token=None, username=None, password=None):
        self.account = None
        if token:
            self.token = token
        else:
            self.token = SETTINGS.get('token')
        if username:
            self.username = username
        else:
            self.username = SETTINGS.get('username')
        if password:
            self.password = password
        else:
            self.password = SETTINGS.get("password")
        try:
            if self.token:
                self.account = GitHub(self.token)
            elif self.username and self.password:
                self.account = GitHub(self.username, self.password)
            else:
                raise Exception("Incomplete Information, please check your setting file")
        except:
            raise Exception("GitHub Account Initialization not successful")

    def get_github_repo_name(self):
        '''
        Find the repo name. It essentially does two attempts:
        - First it try the open folder's name
        - If the first attempt fails, it tries to run "git config --get remote.origin.url" in current directory
        '''
        open_folders = sublime.Window.folders()
        repo_name = None
        if open_folders:
            for folder_path in open_folders:
                path, folder_name = os.path.split(folder)
                if self.account['self.username'][folder_name].get()[0] == 200:
                    repo_name = folder_name
                    break
        file_name = sublime.active_view().file_name()
        folder = os.path.abspath(os.path.dirname(file_name))
        cmd = ['git', '-C', folder, 'config', '--get', 'remote.origin.url']
        try:
            repo_url = subprocess.check_output(' '.join(cmd), shell=True)
            _, raw_repo_name = os.path.split(repo_url)
            raw_repo_name = raw_repo_name.replace("\n", "")
            repo_name = raw_repo_name.replace("\r", "")
        except:
            raise Exception("Error in find repo URL!")
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        return repo_name





