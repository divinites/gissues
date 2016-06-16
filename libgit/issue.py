from . import utils
import sublime

class IssueList(utils.Account):
    def get_list(self,
                 filter=None,
                 state=None,
                 labels=None,
                 sort=None,
                 direction=None,
                 since=None):
        if not filter:
            filter = 'assigned'
        if not state:
            state = 'open'
        if not sort:
            sort = 'created'
        if not direction:
            direction = 'desc'
        repo_name = self.get_github_repo_name()
        response, issue_list = self.account[self.username][
            repo_name].issues.get(filter=filter,
                                  state=state,
                                  sort=sort,
                                  direction=direction)
        if response == 200:
            return issue_list
        else:
            return False

    def print(self, issue_list):
        if issue_list:
            sublime.