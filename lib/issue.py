from . import github
from . import utils

class IssueList:
    def __init__(self, account):
        self.issues = account.repos(utils.get_user())(utils.get_repo_name()).issues

    def get(self):


