import requests
import os
import subprocess
from .utils import find_git
from .. import github_logger
import re


class GitHubAccount:
    def __init__(self, settings):
        self.session = requests.Session()
        self.settings = settings
        api_token = self.settings.get('token', '')
        github_logger.info("The first 8 digits of your GitHub Token is {}".format(api_token[:8]))
        self.username = self.settings.get('username', '')
        github_logger.info("Your own username is {}".format(self.username))
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
                joint_url = '/'.join([API_URL, username, repo_name, 'issues'])

            else:
                joint_url = '/'.join([API_URL, username, repo_name, 'issues', issue_number])
            github_logger.info("the joint url is " + joint_url)
            return joint_url
        else:
            raise Exception("Please check whether the repo_name is correct.")


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
        except:
            return (-1, -1)
        repo_url = repo_url.decode('utf-8')
        github_logger.info("repo address is " + repo_url)
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
    github_logger.info("find username {} and repo_name {}".format(username, repo_name))
    return (username, repo_name)
