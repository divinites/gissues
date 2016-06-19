from . import github
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

    def print_list(self, response):
        if response.status_code == 200:
            print_in_view = PrintListInView(response.json())
            print_in_view.start()

    def print_issue(self, response_list):
        if response_list[0].status_code == 200:
            issue = response_list[0].json()
            comments = response_list[1].json()
            print_in_view = PrintIssueInView(issue, comments)
            print_in_view.start()


class PrintListInView(threading.Thread):
    def __init__(self, issue_list):
        super(PrintListInView, self).__init__(self)
        self.list = issue_list

    def run(self):
        snippet = ''
        snippet += 'Issue ID' + '     ' + 'Issue Title\n'
        for issue in self.list:
            snippet += "{:<12}{}\n".format(issue['number'], issue['title'])
        view = sublime.active_window().new_file()
        view.run_command("insert_snippet", {"contents": snippet})
        view.set_read_only(True)


class PrintIssueInView(threading.Thread):
    def __init__(self, issue, comments):
        super(PrintIssueInView, self).__init__(self)
        self.issue = issue
        self.comments = comments

    def run(self):
        snippet = ''
        snippet += "# Title:         " + self.issue["title"] + '\n'
        snippet += "## ID:           " + str(self.issue['number']) + "\n"
        snippet += "## State:        " + self.issue['state'] + '\n'
        snippet += "## Locked:       " + str(self.issue['locked']) + '\n'
        snippet += "## Assigned to:  " + str(self.issue['assignee']) + "\n"
        snippet += "\n"
        snippet += self.issue['body'] + '\n'
        snippet += "\n"
        for comment in self.comments:
            snippet += "## Comment ID:  " + str(comment['id']) + '\n'
            snippet += "*commented by " + comment['user'][
                'login'] + "   UpdateTime: " + comment['updated_at'] + '*\n'
            snippet += comment['body'] + '\n'
            snippet += "\n"
        snippet += "## Add New Comment:\n"
        view = sublime.active_window().new_file()
        view.set_syntax_file(
            'Packages/Markdown Extended/Syntaxes/Markdown Extended.sublime-syntax')
        view.settings.set('color_scheme', 'Packages/MarkdownEditing/Markdown.tmLanguage')
        view.run_command("insert_snippet", {"contents": snippet})


class ReadIssue(threading.Thread):
    def __init__(self, view):
        pass

    def run(self):
        pass


class PostIssue(threading.Thread):
    def __init__(self, issue):
        pass

    def run(self):
        pass
