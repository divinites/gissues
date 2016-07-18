from .github import GitHubAccount, get_github_repo_info
from .utils import LINE_ENDS, get_issue_post, compare_issues, log
from .utils import format_issue, format_comment, find_comment_region
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

    def delete_comment(self, comment_id, **params):
        issue_url = self.github_account.join_issue_url(
            username=self.username,
            repo_name=self.repo_name)
        return self.github_account.session.delete(
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
            view.run_command("set_file_type",
                             {"syntax":
                              "Packages/{}/list.sublime-syntax".format(__package__)})
            view.settings().set('color_scheme',
                                "Packages/{}/list.tmTheme".format(__package__))
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
            snippet += format_issue(issue)
            comment_dict = {}
            for comment in comments:
                comment_dict[comment['id']] = comment
                snippet += format_comment(comment)
            snippet += "## Add New Comment:" + LINE_ENDS
            snippet += LINE_ENDS
            snippet += "*" + "-" * 10 + "END" + '-' * 10 + "*"
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
            self.view.run_command("set_file_type",
                                  {"syntax":
                                   "Packages/{}/issue.tmLanguage".format(__package__)})
            self.view.run_command("insert_issue", {"issue": snippet})

            self.view.set_scratch(True)


class IssueManipulate(threading.Thread):
    def __init__(self, view=None, issue_dict=None, issue_list=None):
        super(IssueManipulate, self).__init__(self)
        if not view:
            self.view = sublime.active_window().active_view()
        else:
            self.view = view
        self.issue_dict = issue_dict
        self.issue_list = issue_list


class PostNewIssue(IssueManipulate):
    def run(self):
        issue_post = get_issue_post(self.view)
        log("preparing updating issue " + str(issue_post['issue']))
        post_result = self.issue_list.post_issue(
            data=json.dumps(issue_post['issue']))
        if post_result.status_code in (200, 201):
            sublime.status_message("Issue Posted")
            if self.issue_dict:
                issue_dict = self.issue_dict.get()
            issue_dict[self.view.id()] = {'issue': post_result.json(), 'comments': {}}
            self.issue_dict.put(issue_dict)
            issue = post_result.json()
            snippet = format_issue(issue)
            snippet += "## Add New Comment:" + LINE_ENDS
            snippet += LINE_ENDS
            snippet += "*" + "-" * 10 + "END" + '-' * 10 + "*"
            self.view.run_command("clear_view")
            self.view.run_command("set_file_type",
                                  {"syntax":
                                   "Packages/{}/issue.tmLanguage".format(__package__)})
            self.view.run_command("insert_issue", {"issue": snippet})
            self.view.run_command("insert_issue",
                                  {"start_point": self.view.size(),
                                   "issue":
                                   "\n*<Issue number {} created at {}>*".format(
                                       str(post_result.json()['id']),
                                       post_result.json()['created_at'])})
        else:
            sublime.status_message("Issue not Posted, please try again.")


class UpdateIssue(IssueManipulate):
    def run(self):
        view_id = self.view.id()
        issue_dict = self.issue_dict.get()
        original_issue = issue_dict[view_id]
        last_updated_time = original_issue['issue']['updated_at']
        modified_issue = get_issue_post(self.view)
        issue_change, comment_change, deleted_comments = compare_issues(original_issue,
                                                                        modified_issue)
        if issue_change:
            updating_issue = self.issue_list.update_issue(
                original_issue['issue']['number'],
                data=json.dumps(issue_change))
            if updating_issue.status_code in (200, 201):
                sublime.status_message("Issue updated")
                issue_dict[view_id]['issue'] = updating_issue.json()
                if updating_issue.json()['updated_at'] != last_updated_time:
                    self.view.run_command("insert_issue",
                                          {"start_point": self.view.size(),
                                           "issue":
                                           "\n*<Issue number {} updated at {}>*".format(
                                               str(updating_issue.json()['id']),
                                               updating_issue.json()['updated_at'])})
            else:
                sublime.status_message("Issue update fails")
                log("issue update fails, error code " + str(
                    updating_issue.status_code))
        if comment_change:
            for comment_id, content in comment_change.items():
                updating_comment = self.issue_list.update_comment(
                    comment_id=comment_id,
                    data=json.dumps({'body': content}))
                if updating_comment.status_code in (200, 201):
                    sublime.status_message("Comment updated")
                    issue_dict[view_id]["comments"][comment_id] = updating_comment.json()
                    self.view.run_command("insert_issue",
                                          {"start_point": self.view.size(),
                                           "issue":
                                           "\n*<Comment ID {} updated at {}>*".format(
                                               str(comment_id),
                                               updating_comment.json()['updated_at'])})
                else:
                    sublime.status_message("Comment update fails")
                    log("issue update fails, error code " + str(
                        updating_comment.status_code))
        if deleted_comments:
            for comment_id in deleted_comments:
                deleted_comment = self.issue_list.delete_comment(comment_id=comment_id)
                if deleted_comment.status_code == 204:
                    del issue_dict[view_id]["comments"][comment_id]
                    sublime.status_message("Comment deleted.")
                    self.view.run_command("insert_issue",
                                          {"start_point": self.view.size(),
                                           "issue":
                                           "\n*<Comment ID {} deleted.>*".format(
                                               str(comment_id))})
                else:
                    sublime.status_message("Fail to delete comment!")
        if modified_issue['new_comment']:
            new_comment = self.issue_list.post_comment(
                modified_issue['issue']['number'],
                data=json.dumps({'body': modified_issue['new_comment']}))
            if new_comment.status_code in (200, 201):
                sublime.status_message("Comment Posted")
                issue_dict[view_id]["comments"][new_comment.json()['id']] = new_comment.json()
                snippet = format_comment(new_comment.json())
                snippet += "## Add New Comment:" + LINE_ENDS
                snippet += LINE_ENDS
                snippet += "*" + "-" * 10 + "END" + '-' * 10 + "*"
                a, b = find_comment_region(self.view)
                self.view.run_command("replace_issue", {"start": a, "end": b, "snippet": snippet})
                self.view.run_command("insert_issue",
                                      {"start_point": self.view.size(),
                                       "issue":
                                       "\n*<Comment ID {} created at {}>*".format(
                                           str(new_comment.json()['id']),
                                           new_comment.json()['created_at'])})
                comment_id = new_comment.json()['id']
                log("new comment id is " + str(comment_id))

            else:
                sublime.status_message("Comment post fails")
                log("comment post fails, error code " + str(
                    new_comment.status_code))
        self.issue_dict.put(issue_dict)
