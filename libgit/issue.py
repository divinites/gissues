from .github import GitHubAccount
from .. import parameter_container as pc
from .. import github_logger
from .. import global_person_list, global_title_list
from .utils import get_issue_post, compare_issues, restock, show_stock
from .utils import format_issue, format_comment, find_comment_region, find_list_region
from .utils import ViewConverter
import sublime
import threading
import json
import random


class AcquireIssueTitle(threading.Thread):
    def __init__(self, issue_obj):
        super(AcquireIssueTitle, self).__init__(self)
        self.issue_obj = IssueObj(issue_obj.settings, issue_obj.username,
                                  issue_obj.repo_name)

    def run(self):
        title_list = []
        self.issue_obj.get(params={"state": "all"})
        while True:
            for issue in self.issue_obj.issue_response.json():
                title_list.append((issue['title'], issue['number']))
            links = self.issue_obj.get_links()
            if (not links) or 'next' not in links:
                break
            else:
                self.issue_obj.get(links['next']['url'])
        global_title_list["{}/{}".format(self.issue_obj.username,
                                         self.issue_obj.repo_name)] = sorted(
                                             title_list, key=lambda x: x[1])


class IssueObj:
    def __init__(self, settings, username=None, repo_name=None):
        self.github_account = GitHubAccount(settings)
        self.settings = settings
        self.repo_name = repo_name
        self.username = username
        self.issue_response = None
        self.total_page_number = 1
        self.current_page_number = 1
        self.links = None

    def get_repo(self, username, repo_name):
        self.username = username
        self.repo_name = repo_name

    def find_repo(self, view, repo_info_storage):
        view_id = view.id()
        try:
            github_logger.info("try to find the view in repo_dictionary...")
            github_logger.info("repo_info_storage contains {}".format(
                show_stock(repo_info_storage, view_id)))
            self.username, self.repo_name, self.issue_response = show_stock(
                repo_info_storage, view_id)
        except:
            raise Exception("Which repository should I post?")

    def get(self, issue_url=None, **params):
        if not issue_url:
            issue_url = self.github_account.join_issue_url(
                username=self.username, repo_name=self.repo_name)
        self.issue_response = self.github_account.session.get(issue_url,
                                                              **params)
        return self.issue_response

    def get_links(self, **params):
        if not self.issue_response:
            self.get(**params)
        return self.issue_response.links

    def post_issue(self, **params):
        issue_url = self.github_account.join_issue_url(
            username=self.username, repo_name=self.repo_name)
        return self.github_account.session.post(issue_url, **params)

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
            username=self.username, repo_name=self.repo_name)
        return self.github_account.session.patch(
            issue_url + '/comments/' + str(comment_id), **params)

    def delete_comment(self, comment_id, **params):
        issue_url = self.github_account.join_issue_url(
            username=self.username, repo_name=self.repo_name)
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

    def replace_labels(self, issue_number, labels):
        issue_url = self.github_account.join_issue_url(
            username=self.username,
            repo_name=self.repo_name,
            issue_number=str(issue_number))
        issue_url += "/labels"
        github_logger.info("replace label url is {}".format(issue_url))
        if len(labels) == 1 and labels[0] == '':
            return self.github_account.session.delete(issue_url)
        return self.github_account.session.put(issue_url, json=labels)

    def get_all_labels(self):
        issue_url = self.github_account.join_issue_url(
            username=self.username, repo_name=self.repo_name)
        issue_url = issue_url[:-7]
        issue_url += "/labels"
        labels = set([])
        label_resp = self.github_account.session.get(issue_url)
        if label_resp.status_code != 200:
            raise Exception("cannot get labels")
        for label in label_resp.json():
            labels.add(label['name'])
        return labels

    def get_labels(self, issue_number):
        pass


    def generate_labels(self, labels):
        issue_url = self.github_account.join_issue_url(
            username=self.username, repo_name=self.repo_name)
        issue_url += "/labels"
        for label in labels:
            color = "#%06x" % random.randint(0, 0xFFFFFF)
            label_resp = self.github_account.session.post(issue_url, data={"color": color, "name": label})
            if label_resp.status_code != 201:
                raise Exception("error creating label {}".format(label))


class PrintListInView(threading.Thread):
    def __init__(self,
                 view,
                 issue_list,
                 repo_info_storage,
                 command=None,
                 new_flag=True,
                 **args):
        super(PrintListInView, self).__init__(self)
        self.issue_list = issue_list
        self.args = args
        self.repo_info_storage = repo_info_storage
        self.view = view
        self.command = command
        self.new_flag = new_flag

    def run(self):
        if not self.new_flag:
            if not self.issue_list.issue_response:
                self.issue_list.get(params=self.args)
            else:
                _, _, self.issue_list.issue_response = show_stock(
                    self.repo_info_storage, self.view.id())
                if self.command:
                    links = self.issue_list.get_links()
                    if self.command in links:
                        self.issue_list.get(links[self.command]['url'],
                                            params=self.args)
                    else:
                        pass
        else:
            self.issue_list.get(params=self.args)
        issue_response = self.issue_list.issue_response
        if issue_response.status_code in (200, 201):
            json_list = issue_response.json()
            snippet = '\n'
            for issue in json_list:
                snippet += "{:<12}{:<10}{}".format(
                    str(issue['number']), issue['locked'],
                    issue['title']) + pc.line_ends
            start_point, end_point = find_list_region(self.view)
            if self.view.is_read_only():
                self.view.set_read_only(False)
            self.view.run_command("replace_snippet", {"snippet": snippet,
                                                      "start_point":
                                                      start_point,
                                                      "end_point": end_point})
            self.view.sel().clear()
            view_converter = ViewConverter(self.view)
            start = view_converter.get_line_regions()[3].a
            self.view.sel().add(sublime.Region(start, start))
            self.view.set_read_only(True)
            restock(self.repo_info_storage, self.view.id(),
                    (self.issue_list.username, self.issue_list.repo_name,
                     issue_response))
        else:
            sublime.status_message("Cannot obtain issue list, error code {}".
                                   format(str(issue_response.status_code)))


class PrintIssueInView(threading.Thread):
    def __init__(self,
                 issue_list,
                 issue_number,
                 issue_storage,
                 repo_info,
                 repo_info_storage,
                 view=None):
        super(PrintIssueInView, self).__init__(self)
        self.issue_list = issue_list
        self.issue_number = issue_number
        self.issue_storage = issue_storage
        self.repo_info = repo_info
        self.repo_info_storage = repo_info_storage
        self.view = view

    def run(self):
        issue_response, comments_response = self.issue_list.get_issue(
            self.issue_number)
        if issue_response.status_code in (200, 201):
            issue = issue_response.json()
            comments = comments_response.json()
            user_set = set([])
            label_set = set([])
            for label_info in issue['labels']:
                label_set.add(label_info['name'])
            user_set.add(issue['user']['login'])
            snippet = ''
            snippet += format_issue(issue)
            comment_dict = {}
            for comment in comments:
                user_set.add(comment['user']['login'])
                comment_dict[comment['id']] = comment
                snippet += format_comment(comment)
            snippet += "## Add New Comment:" + pc.line_ends
            snippet += pc.line_ends
            snippet += "*" + "-" * 10 + "END" + '-' * 10 + "*"
            if not self.view:
                self.view = sublime.active_window().new_file()
            global_person_list[self.view.id()] = user_set
            github_logger.info("person list is {}".format(str(global_person_list)))
            restock(self.issue_storage, self.view.id(), {"issue": issue,
                                                         "label": label_set,
                                                         "comments":
                                                         comment_dict})
            restock(self.repo_info_storage, self.view.id(),
                    (self.repo_info[0], self.repo_info[1], issue_response))
            self.view.run_command("erase_snippet")
            self.view.run_command("set_file_type", {"syntax": pc.issue_syntax})
            self.view.run_command("insert_issue_snippet", {"snippet": snippet})
            view_converter = ViewConverter(self.view)
            _, a, b, _ = view_converter.find_region_line("## Add New Comment:", "*" + "-" * 10 + "END")
            self.view.sel().clear()
            if b > a:
                self.view.sel().add(sublime.Region(a + 1, a + 1))
            else:
                self.view.sel().add(sublime.Region(a, a))
            self.view.set_scratch(True)


class IssueManipulate(threading.Thread):
    def __init__(self, view=None, issue_storage=None, issue_list=None):
        super(IssueManipulate, self).__init__(self)
        if not view:
            self.view = sublime.active_window().active_view()
        else:
            self.view = view
        self.issue_storage = issue_storage
        self.issue_list = issue_list


class PostNewIssue(IssueManipulate):
    def run(self):
        issue_post = get_issue_post(self.view)
        github_logger.info("preparing updating issue " + str(issue_post[
            'issue']))
        post_result = self.issue_list.post_issue(
            data=json.dumps(issue_post['issue']))
        if post_result.status_code in (200, 201):
            sublime.status_message("Issue Posted")
            if self.issue_storage:
                restock(self.issue_storage, self.view.id(),
                        {'issue': post_result.json(),
                         'comments': {}})
            issue = post_result.json()
            snippet = format_issue(issue)
            github_logger.info("format issue")
            snippet += "## Add New Comment:" + pc.line_ends
            snippet += pc.line_ends
            snippet += "*" + "-" * 10 + "END" + '-' * 10 + "*"
            self.view.run_command("erase_snippet")
            self.view.run_command("set_file_type", {"syntax": pc.issue_syntax})
            self.view.run_command("insert_issue_snippet", {"snippet": snippet})
            github_logger.info("set syntax")
            self.view.run_command(
                "insert_issue_snippet",
                {"start_point": self.view.size(),
                 "snippet": "\n*<Issue number {} created at {}>*".format(
                     str(post_result.json()['id']),
                     post_result.json()['created_at'])})
        else:
            sublime.status_message(
                "Issue not Posted, error code {} please try again.".format(
                    str(post_result.status_code)))


class UpdateIssue(IssueManipulate):
    def run(self):
        view_id = self.view.id()
        original_issue = show_stock(self.issue_storage, view_id)
        github_logger.info("take out original issue")
        last_updated_time = original_issue['issue']['updated_at']
        modified_issue = get_issue_post(self.view)
        github_logger.info("get the modified issue")
        issue_change, label_change, comment_change, deleted_comments = compare_issues(
            original_issue, modified_issue)
        if issue_change:
            updating_issue = self.issue_list.update_issue(
                original_issue['issue']['number'],
                data=json.dumps(issue_change))
            if updating_issue.status_code in (200, 201):
                sublime.status_message("Issue updated")
                original_issue['issue'] = updating_issue.json()
                if updating_issue.json()['updated_at'] != last_updated_time:
                    self.view.run_command(
                        "insert_issue_snippet",
                        {"start_point": self.view.size(),
                         "snippet":
                         "\n*<Issue number {} updated at {}>*".format(
                             str(updating_issue.json()['id']),
                             updating_issue.json()['updated_at'])})
            else:
                sublime.status_message("Issue update fails")
                github_logger.info("issue update fails, error code " + str(
                    updating_issue.status_code))
        if label_change != -1:
            github_logger.info("new labels are {}".format(repr(label_change)))
            self.issue_list.replace_labels(original_issue['issue']['number'], list(label_change))
        if comment_change:
            for comment_id, content in comment_change.items():
                updating_comment = self.issue_list.update_comment(
                    comment_id=comment_id, data=json.dumps({'body': content}))
                if updating_comment.status_code in (200, 201):
                    sublime.status_message("Comment updated")
                    original_issue["comments"][
                        comment_id] = updating_comment.json()
                    self.view.run_command(
                        "insert_issue_snippet",
                        {"start_point": self.view.size(),
                         "snippet": "\n*<Comment ID {} updated at {}>*".format(
                             str(comment_id),
                             updating_comment.json()['updated_at'])})
                else:
                    sublime.status_message("Comment update fails")
                    github_logger.info("issue update fails, error code " + str(
                        updating_comment.status_code))
        if deleted_comments:
            for comment_id in deleted_comments:
                deleted_comment = self.issue_list.delete_comment(
                    comment_id=comment_id)
                if deleted_comment.status_code == 204:
                    del original_issue["comments"][comment_id]
                    sublime.status_message("Comment deleted.")
                    self.view.run_command("insert_issue_snippet", {
                        "start_point": self.view.size(),
                        "snippet":
                        "\n*<Comment ID {} deleted.>*".format(str(comment_id))
                    })
                else:
                    sublime.status_message("Fail to delete comment!")
        if modified_issue['new_comment']:
            new_comment = self.issue_list.post_comment(
                modified_issue['issue']['number'],
                data=json.dumps({'body': modified_issue['new_comment']}))
            if new_comment.status_code in (200, 201):
                sublime.status_message("Comment Posted")
                original_issue["comments"][new_comment.json()[
                    'id']] = new_comment.json()
                snippet = format_comment(new_comment.json())
                snippet += "## Add New Comment:" + pc.line_ends
                snippet += pc.line_ends
                snippet += "*" + "-" * 10 + "END" + '-' * 10 + "*"
                a, b = find_comment_region(self.view)
                github_logger.info("insert the snippet")
                self.view.run_command("replace_snippet", {"start_point": a,
                                                          "end_point": b,
                                                          "snippet": snippet})
                self.view.run_command(
                    "insert_issue_snippet",
                    {"start_point": self.view.size(),
                     "snippet": "\n*<Comment ID {} created at {}>*".format(
                         str(new_comment.json()['id']),
                         new_comment.json()['created_at'])})
                comment_id = new_comment.json()['id']
                github_logger.info("new comment id is " + str(comment_id))

            else:
                sublime.status_message("Comment post fails")
                github_logger.info("comment post fails, error code " + str(
                    new_comment.status_code))
        restock(self.issue_storage, view_id, original_issue)
