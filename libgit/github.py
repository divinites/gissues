import requests
import os
from .. import log


class GitHubAccount:

    def __init__(self, settings):
        self.session = requests.Session()
        self.settings = settings
        api_token = self.settings.get('token', '')
        log("The first 8 digits of your GitHub Token is {}".format(
            api_token[:8]))
        self.username = self.settings.get('username', '')
        log("Your own username is {}".format(self.username))
        password = self.settings.get('password', '')
        if api_token:
            self.session.headers['Authorization'] = 'token %s' % api_token
        elif self.username and password:
            self.session.auth = (self.username, password)
        else:
            raise Exception("Please check the authentication settings!")
        self.session.headers['content-type'] = 'application/json'

    def join_url(self, username=None, repo_name=None, sequence=None):
        API_URL = 'https://api.github.com/repos'
        if not username:
            username = self.username
        if repo_name:
            url = [API_URL, username, repo_name]
            url.extend(sequence)
            joint_url = '/'.join(url)
            log("the joint url is " + joint_url)
            return joint_url
        else:
            raise Exception("Please check whether the repo_name is correct.")


def get_github_repo_info(folder_path):
    '''
    Find the repo name. It essentially does two attempts:
    - First it try the open folder's name
    - If the first attempt fails, it tries to run "git config --get remote.origin.url" in current directory
    '''
    # cmd = [git, '-C', folder_path, 'config', '--get', 'remote.origin.url']
    # try:
    #     try:
    #         repo_url = subprocess.check_output(' '.join(cmd), shell=True)
    #     except:
    if not is_git_dir(folder_path):
        return (-1, -1)
    else:
        username = ''
        raw_repo_name = ''
        with open(os.path.join(folder_path, ".git", "config")) as git_config_file:
            for line in git_config_file.readlines():
                if line.strip().startswith("url"):
                    residuals, raw_repo_name = os.path.split(line)
                    _, username = os.path.split(residuals)
                    break
            else:
                raise Exception('repo URL error!')
        raw_repo_name = raw_repo_name.replace("\n", "")
        repo_name = raw_repo_name.replace("\r", "")

    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    log("find username {} and repo_name {}".format(username, repo_name))
    return (username, repo_name)


def is_git_dir(folder):
    for dir_path, dir_names, file_names in os.walk(folder):
        if dir_path == folder and ".git" in dir_names:
            return True
    return False


