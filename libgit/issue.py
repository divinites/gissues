from . import github
from . import utils
from .utils import LINE_ENDS
import sublime
import threading


class IssueList:
    def __init__(self, settings):
        self.github_account = github.GitHubAccount(settings)
        self.repo_name = None
        # self.repo_name = 'github-issues'

    def find_repo(self):
        self.repo_name = github.get_github_repo_name()

    def get(self, **params):
        issue_list_url = self.github_account.join_issue_url(
            repo_name=self.repo_name)
        return self.github_account.session.get(issue_list_url, **params)

    def get_issue(self, issue_number, **params):
        issue_url = self.github_account.join_issue_url(
            repo_name=self.repo_name,
            issue_number=str(issue_number))
        return (
            self.github_account.session.get(issue_url, **params),
            self.github_account.session.get(issue_url + '/comments', **params))


class PrintListInView(threading.Thread):
    def __init__(self, issue_list):
        super(PrintListInView, self).__init__(self)
        self.issue_list = issue_list

    def run(self):
        issue_response = self.issue_list.get()
        if issue_response.status_code == 200:
            json_list = issue_response.json()
            snippet = ''
            snippet += 'Issue ID' + '     ' + 'Locked    ' + 'Issue Title' + LINE_ENDS
            for issue in json_list:
                snippet += "{:<12}{:<10}{}".format(str(issue['number']),issue['locked'], issue['title']) + LINE_ENDS
            view = sublime.active_window().new_file()
            view.run_command("insert_snippet", {"contents": snippet})
            view.set_read_only(True)
            view.set_scratch(True)
        else:
            sublime.status_message("Cannot obtain issue list, error code {}".format(str(issue_response.status_code)))


class PrintIssueInView(threading.Thread):
    def __init__(self, issue_list, issue_number, issue_dict):
        super(PrintIssueInView, self).__init__(self)
        self.issue_list = issue_list
        self.issue_number = issue_number
        self.issue_dict = issue_dict

    def run(self):
        issue_response, comments_response = self.issue_list.get_issue(self.issue_number)
        if issue_response.status_code == 200:
            issue = issue_response.json()
            comments = comments_response.json()
            snippet = ''
            snippet += "# Title:         " + issue["title"] + LINE_ENDS
            snippet += "## ID:           " + str(issue['number']) + LINE_ENDS
            snippet += "## State:        " + issue['state'] + LINE_ENDS
            snippet += "## Locked:       " + str(issue['locked']) + LINE_ENDS
            snippet += "## Assigned to:  " + str(issue['assignee']) + LINE_ENDS
            snippet += LINE_ENDS
            snippet += utils.filter_line_ends(issue['body']) + LINE_ENDS
            snippet += LINE_ENDS
            for comment in comments:
                snippet += "## Comment ID:  " + str(comment['id']) + LINE_ENDS
                snippet += "*commented by " + comment['user'][
                    'login'] + "   UpdateTime: " + comment['updated_at'] + '*' + LINE_ENDS
                snippet += utils.filter_line_ends(comment['body']) + LINE_ENDS
                snippet += LINE_ENDS
            snippet += "## Add New Comment:" + LINE_ENDS
            view = sublime.active_window().new_file()
            self.issue_dict[view.id()] = {"issue": issue, "comments": comments}
            view.set_syntax_file(
                'Packages/Markdown Extended/Syntaxes/Markdown Extended.sublime-syntax')
            # view.settings.set('color_scheme', 'Packages/MarkdownEditing/Markdown.tmLanguage')
            view.run_command("set_file_type", {"syntax": "Packages/MarkdownEditing/Markdown.tmLanguage"})
            view.run_command("insert_issue", {"issue": snippet})


class ReadIssue(threading.Thread):
    def __init__(self, view):
        self.view = view

    def run(self):
        pass


class PostIssue(threading.Thread):
    def __init__(self, issue):
        pass

    def run(self):
        pass
