from .github import GitHubAccount, get_github_repo_info
from .utils import LINE_ENDS, filter_line_ends, get_issue_post, compare_issues, log
import sublime
import threading
import json


class IssueList:
    def __init__(self, settings):
        self.github_account = GitHubAccount(settings)
        self.repo_name = None
        self.username = None
        # self.repo_name = 'github-issues'

    def find_repo(self):
        self.username, self.repo_name = get_github_repo_info()
        log("username and repo_name are {} and {}".format(self.username,
                                                          self.repo_name))

    def get(self, **params):
        issue_list_url = self.github_account.join_issue_url(
            username=self.username,
            repo_name=self.repo_name)
        return self.github_account.session.get(issue_list_url, **params)

    def post_issue(self, **params):
        issue_list_url = self.github_account.join_issue_url(
            username=self.username,
            repo_name=self.repo_name)
        return self.github_account.session.post(issue_list_url, **params)

    def update_issue(self, issue_number, **params):
        issue_url = self.github_account.join_issue_url(
            username=self.username,
            repo_name=self.repo_name,
            issue_number=str(issue_number))
        return self.github_account.session.patch(issue_url, **params)

    def post_comment(self, issue_number, **params):
        issue_url = self.github_account.join_issue_url(
            username=self.username,
            repo_name=self.repo_name,
            issue_number=str(issue_number))
        return self.github_account.session.post(issue_url + '/comments',
                                                **params)

    def update_comment(self, comment_id, **params):
        issue_url = self.github_account.join_issue_url(
            username=self.username,
            repo_name=self.repo_name)
        return self.github_account.session.patch(
            issue_url + '/comments/' + str(comment_id), **params)

    def get_issue(self, issue_number, **params):
        issue_url = self.github_account.join_issue_url(
            username=self.username,
            repo_name=self.repo_name,
            issue_number=str(issue_number))
        return (
            self.github_account.session.get(issue_url, **params),
            self.github_account.session.get(issue_url + '/comments', **params))


class PrintListInView(threading.Thread):
    def __init__(self, issue_list, **args):
        super(PrintListInView, self).__init__(self)
        self.issue_list = issue_list
        self.args = args

    def run(self):
        issue_response = self.issue_list.get(params=self.args)
        if issue_response.status_code in (200, 201):
            json_list = issue_response.json()
            snippet = ''
            snippet += 'Issue No.' + '   ' + 'Locked    ' + 'Issue Title' + LINE_ENDS
            for issue in json_list:
                snippet += "{:<12}{:<10}{}".format(
                    str(issue['number']), issue['locked'],
                    issue['title']) + LINE_ENDS
            view = sublime.active_window().new_file()
            view.run_command("clear_view")
            view.run_command(
                "set_file_type",
                {"syntax": "Packages/gissues/list.sublime-syntax"})
            view.settings().set('color_scheme', "Packages/gissues/list.tmTheme")
            view.run_command("insert_issue", {"issue": snippet})

            view.set_read_only(True)
            view.set_scratch(True)
        else:
            sublime.status_message(
                "Cannot obtain issue list, error code {}".format(str(
                    issue_response.status_code)))


class PrintIssueInView(threading.Thread):
    def __init__(self, issue_list, issue_number, issue_dict, view=None):
        super(PrintIssueInView, self).__init__(self)
        self.issue_list = issue_list
        self.issue_number = issue_number
        self.issue_dict = issue_dict
        self.view = view

    def run(self):
        issue_response, comments_response = self.issue_list.get_issue(
            self.issue_number)
        if issue_response.status_code in (200, 201):
            issue = issue_response.json()
            comments = comments_response.json()
            snippet = ''
            snippet += "# Title         : " + issue["title"] + LINE_ENDS
            snippet += "## Number       : " + str(issue['number']) + LINE_ENDS
            snippet += "## State        : " + issue['state'] + LINE_ENDS
            snippet += "## Locked       : " + str(issue['locked']) + LINE_ENDS
            snippet += "## Assignee     : " + str(issue[
                'assignee']) + LINE_ENDS
            snippet += '-' * 10 + "Content" + '-' * 10 + LINE_ENDS
            snippet += filter_line_ends(issue['body']) + LINE_ENDS
            # snippet += LINE_ENDS
            comment_dict = {}
            for comment in comments:
                comment_dict[comment['id']] = comment['body']
                snippet += "## Comment ID:  " + str(comment['id']) + LINE_ENDS
                snippet += "*commented by " + comment['user'][
                    'login'] + "   UpdateTime: " + comment[
                        'updated_at'] + '*' + LINE_ENDS
                snippet += filter_line_ends(comment['body']) + LINE_ENDS
                # snippet += LINE_ENDS
            snippet += "## Add New Comment:" + LINE_ENDS
            if not self.view:
                self.view = sublime.active_window().new_file()
            issue_dict = self.issue_dict.get()
            issue_dict[self.view.id()] = {"issue": issue,
                                          "comments": comment_dict}
            # view.set_syntax_file(
            #     'Packages/Markdown Extended/Syntaxes/Markdown Extended.sublime-syntax')
            # view.settings.set('color_scheme', 'Packages/MarkdownEditing/Markdown.tmLanguage')
            self.issue_dict.put(issue_dict)
            self.view.run_command("clear_view")
            self.view.run_command(
                "set_file_type",
                {"syntax": "Packages/gissues/issue.tmLanguage"})
            self.view.run_command("insert_issue", {"issue": snippet})

            self.view.set_scratch(True)


class IssueManipulate(threading.Thread):
    def __init__(self, view=None, issue_dict=None, issue_list=None):
        super(IssueManipulate, self).__init__(self)
        if not view:
            self.view = sublime.active_window().active_view()
        self.issue_dict = issue_dict
        self.issue_list = issue_list


class PostNewIssue(IssueManipulate):
    def run(self):
        issue_post = get_issue_post(self.view)
        log("preparing updating issue " + str(issue_post['issue']))
        post_result = self.issue_list.post_issue(
            data=json.dumps(issue_post['issue']))
        if post_result.status_code in(200, 201):
            sublime.status_message("Issue Posted")
        else:
            sublime.status_message("Issue not Posted, please try again.")


class UpdateIssue(IssueManipulate):
    def run(self):
        view_id = self.view.id()
        issue_dict = self.issue_dict.get()
        original_issue = issue_dict[view_id]
        modified_issue = get_issue_post(self.view)
        issue_change, comment_change = compare_issues(original_issue,
                                                      modified_issue)
        updating_issue = self.issue_list.update_issue(
            original_issue['issue']['number'],
            data=json.dumps(issue_change))
        if updating_issue.status_code in (200, 201):
            sublime.status_message("Issue updated")
        else:
            sublime.status_message("Issue update fails")
            log("issue update fails, error code " + str(updating_issue.status_code))
        for comment_id, content in comment_change.items():
            updating_comment = self.issue_list.update_comment(
                comment_id=comment_id,
                data=json.dumps({'body': content}))
            if updating_comment.status_code in (200, 201):
                sublime.status_message("Comment updated")
            else:
                sublime.status_message("Comment update fails")
                log("issue update fails, error code " + str(updating_comment.status_code))
        if modified_issue['new_comment']:
            new_comment = self.issue_list.post_comment(
                modified_issue['issue']['number'],
                data=json.dumps({'body': modified_issue['new_comment']}))
            if new_comment.status_code in (200, 201):
                sublime.status_message("Comment Posted")
            else:
                sublime.status_message("Comment post fails")
                log("comment post fails, error code " + str(new_comment.status_code))
        self.issue_dict.put(issue_dict)
        # print_new_issue = PrintIssueInView(self.issue_list, original_issue['issue']['id'], self.issue_dict, view=self.view)
        # print_new_issue.start()
        # class UpdateComment(IssueManipulate):
        #     def run(self, issue_list):
        #         comment_ids, comment_content = ViewConverter.get_comment_list(
        #             self.view_lines, self.crucial_lines)

        # class PostNewComment(IssueManipulate):
        #     def run(self, issue_list):
        #         comment_post = {}
        #         comment_post['body'] = ViewConverter.get_new_comment(
        #             self.view_lines, self.crucial_lines)
        #         issue_list.post_comment(json=json.dumps(comment_post))
