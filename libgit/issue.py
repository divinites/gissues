from .github import GitHubAccount
from .. import log, LINE_END, settings
from .. import global_person_list, global_title_list, global_label_list, global_commit_list
from .. import repo_info_storage
from .utils import get_issue_post, compare_issues, restock, show_stock
from .utils import format_issue, format_comment, find_comment_region, find_list_region
from .utils import ViewConverter, configure_issue_view
from .. import COMMENT_START, COMMENT_END, ISSUE_START, ISSUE_END, HEADER_END, CONTENT_END, ADD_COMMENT
import threading
import json
import random
import sublime


class AcquireRepoInfo(threading.Thread):

    def __init__(self, username, repo_name):
        super(AcquireRepoInfo, self).__init__(self)
        self.issue_obj = GitRepo(
            sublime.load_settings("github_issue.sublime-settings"), username,
            repo_name)

    def run(self):
        title_list = []
        self.issue_obj.get(params={"state": "all"})
        if self.issue_obj.github_response.status_code not in (200, 201):
            raise Exception(
                "Cannnot find relevant repo info, please check the input!")
        label_list = self.issue_obj.get_all_labels()
        while True:
            for issue in self.issue_obj.github_response.json():
                title_list.append((issue['title'], issue['number'], 0
                                   if issue['state'] == 'open' else 1))
            links = self.issue_obj.get_links()
            if (not links) or 'next' not in links:
                break
            else:
                self.issue_obj.get(links['next']['url'])

        commit_set = self.issue_obj.get_commits()
        while True:
            links = self.issue_obj.get_links()
            if (not links) or 'next' not in links:
                break
            else:
                commit_set.update(
                    self.issue_obj.get_commits(links["next"]["url"]))
        repo_info = "{}/{}".format(self.issue_obj.username,
                                   self.issue_obj.repo_name)
        # if repo_info not in global_title_list:
        log("finish acquiring label, commit and issue title")
        global_title_list[repo_info] = sorted(
            title_list, key=lambda x: (x[2], x[1] * -1))
        global_label_list[repo_info] = label_list
        global_commit_list[repo_info] = commit_set


class GitRepo:

    def __init__(self, settings, username=None, repo_name=None):
        self.github_account = GitHubAccount(settings)
        self.settings = settings
        self.repo_name = repo_name
        self.username = username
        self.github_response = None
        self.links = None

    def get_repo_info(self, username, repo_name):
        self.username = username
        self.repo_name = repo_name

    def find_repo_info(self, view, repo_info_storage):
        view_id = view.id()
        try:
            log("try to find the view in repo_dictionary...")
            log("repo_info_storage contains {}".format(
                show_stock(repo_info_storage, view_id)))
            self.username, self.repo_name, self.github_response = show_stock(
                repo_info_storage, view_id)
        except:
            raise Exception("Which repository should I post?")

    def get(self, issue_url=None, **params):
        if not issue_url:
            issue_url = self.github_account.join_url(username=self.username,
                                                     repo_name=self.repo_name,
                                                     sequence=['issues'])
        self.github_response = self.github_account.session.get(issue_url,
                                                               **params)
        return self.github_response

    def get_links(self, **params):
        if not self.github_response:
            self.get(**params)
        return self.github_response.links

    def post_issue(self, **params):
        issue_url = self.github_account.join_url(username=self.username, repo_name=self.repo_name, sequence=['issues'])
        return self.github_account.session.post(issue_url, **params)

    def update_issue(self, issue_number, **params):
        issue_url = self.github_account.join_url(username=self.username,
                                                 repo_name=self.repo_name,
                                                 sequence=['issues', str(issue_number)])
        return self.github_account.session.patch(issue_url, **params)

    def post_comment(self, issue_number, **params):
        issue_url = self.github_account.join_url(username=self.username,
                                                 repo_name=self.repo_name,
                                                 sequence=['issues', str(issue_number), 'comments'])
        return self.github_account.session.post(issue_url, **params)

    def update_comment(self, comment_id, **params):
        issue_url = self.github_account.join_url(username=self.username,
                                                 repo_name=self.repo_name,
                                                 sequence=['issues', 'comments', str(comment_id)])
        return self.github_account.session.patch(issue_url, **params)

    def delete_comment(self, comment_id, **params):
        issue_url = self.github_account.join_url(username=self.username,
                                                 repo_name=self.repo_name,
                                                 sequence=['issues', 'comments', str(comment_id)])
        return self.github_account.session.delete(issue_url, **params)

    def get_issue_comment(self, issue_number, **params):
        issue_url = self.github_account.join_url(username=self.username,
                                                 repo_name=self.repo_name,
                                                 sequence=['issues', str(issue_number)])
        comment_url = self.github_account.join_url(username=self.username,
                                                   repo_name=self.repo_name,
                                                   sequence=['issues', str(issue_number), 'comments'])
        return (
            self.github_account.session.get(issue_url, **params),
            self.github_account.session.get(comment_url, **params))

    def get_commits(self, issue_url=None):
        if not issue_url:
            issue_url = self.github_account.join_url(username=self.username,
                                                     repo_name=self.repo_name,
                                                     sequence=['commits'])
        commit_set = set([])
        commit_resp = self.get(issue_url)
        if commit_resp.status_code == 200:
            for commit in commit_resp.json():
                commit_set.add((commit['sha'], commit['commit']['message']))
            return commit_set
        elif commit_resp.status_code == 409:
            pass
        else:
            raise Exception("cannot get commits!, error code {}".format(commit_resp.status_code))

    def replace_labels(self, issue_number, labels):
        issue_url = self.github_account.join_url(username=self.username,
                                                 repo_name=self.repo_name,
                                                 sequence=['issues', str(issue_number), 'labels'])
        log("replace label url is {}".format(issue_url))
        if len(labels) == 1 and '' in labels:
            return self.github_account.session.delete(issue_url)
        return self.github_account.session.put(issue_url, json=list(labels))

    def get_all_labels(self):
        issue_url = self.github_account.join_url(username=self.username, repo_name=self.repo_name, sequence=['labels'])
        labels = set([])
        label_resp = self.github_account.session.get(issue_url)
        if label_resp.status_code != 200:
            raise Exception("cannot get labels")
        for label in label_resp.json():
            labels.add(label['name'])
        return labels

    def attach_labels(self, issue_number, labels):
        all_labels = self.get_all_labels()
        new_labels = set(labels).difference(all_labels)
        if len(new_labels) > 0:
            self.generate_labels(new_labels)
        self.replace_labels(issue_number, labels)

    def generate_labels(self, labels):
        issue_url = self.github_account.join_url(username=self.username,
                                                 repo_name=self.repo_name,
                                                 sequence=["labels"])
        for label in labels:
            color = "%06x" % random.randint(0, 0xFFFFFF)
            label_resp = self.github_account.session.post(
                issue_url, json={"color": color,
                                 "name": label})
            log("the generate labels code is {}".format(
                label_resp.status_code))
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
            if not self.issue_list.github_response:
                self.issue_list.get(params=self.args)
            else:
                _, _, self.issue_list.github_response = show_stock(
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
        github_response = self.issue_list.github_response
        if github_response.status_code in (200, 201):
            json_list = github_response.json()
            snippet = '\n'
            for issue in json_list:
                snippet += "{:<12}{:<10}{}".format(
                    str(issue['number']), issue['locked'],
                    issue['title']) + LINE_END
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
                     github_response))
        else:
            sublime.status_message("Cannot obtain issue list, error code {}".
                                   format(str(github_response.status_code)))


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
        github_response, comments_response = self.issue_list.get_issue_comment(
            self.issue_number)
        if github_response.status_code in (200, 201):
            issue = github_response.json()
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
            snippet += ADD_COMMENT + LINE_END
            snippet += LINE_END
            snippet += CONTENT_END
            if not self.view:
                self.view = sublime.active_window().new_file()
            global_person_list[self.view.id()] = user_set
            log("person list is {}".format(
                str(global_person_list)))
            restock(self.issue_storage, self.view.id(), {"issue": issue,
                                                         "label": label_set,
                                                         "comments":
                                                         comment_dict})
            restock(self.repo_info_storage, self.view.id(),
                    (self.repo_info[0], self.repo_info[1], github_response))
            self.view.run_command("erase_snippet",
                                  {"start_point": 0,
                                   "end_point": self.view.size()})
            self.view.run_command("insert_issue_snippet", {"snippet": snippet})
            view_converter = ViewConverter(self.view)
            _, a, b, _ = view_converter.find_region_line(ADD_COMMENT, CONTENT_END)
            self.view.sel().clear()
            if b > a:
                self.view.sel().add(sublime.Region(a + 1, a + 1))
            else:
                self.view.sel().add(sublime.Region(a, a))
            configure_issue_view(self.view)


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
        log("preparing posting issue " + str(issue_post[
            'issue']))
        post_result = self.issue_list.post_issue(
            data=json.dumps(issue_post['issue']))
        if post_result.status_code in (200, 201):
            issue = post_result.json()
            if len(issue_post['label']) != 0:
                self.issue_list.attach_labels(issue['number'],
                                              issue_post['label'])
            repo_info = (self.issue_list.username, self.issue_list.repo_name,
                         None)
            self.view.settings().set("new_issue", False)
            print_issue_in_view = PrintIssueInView(
                self.issue_list, issue['number'], self.issue_storage,
                repo_info, repo_info_storage, self.view)
            print_issue_in_view.start()
        else:
            sublime.status_message(
                "Issue not Posted, error code {} please try again.".format(
                    str(post_result.status_code)))


class UpdateIssue(IssueManipulate):

    def run(self):
        view_id = self.view.id()
        original_issue = show_stock(self.issue_storage, view_id)
        if original_issue:
            log("successfully take out original issue")
        log("take out original issue with title {}".format(
            original_issue['issue']['title']))
        last_updated_time = original_issue['issue']['updated_at']
        modified_issue = get_issue_post(self.view)
        log("get the modified issue")
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
                log("issue update fails, error code " + str(
                    updating_issue.status_code))
        if label_change != -1:
            log("new labels are {}".format(repr(label_change)))
            self.issue_list.attach_labels(original_issue['issue']['number'],
                                          list(label_change))
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
                    log("issue update fails, error code " + str(
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
                snippet += ADD_COMMENT + LINE_END
                snippet += LINE_END
                snippet += CONTENT_END
                a, b = find_comment_region(self.view)
                log("insert the snippet")
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
                log("new comment id is " + str(comment_id))

            else:
                sublime.status_message("Comment post fails")
                log("comment post fails, error code " + str(
                    new_comment.status_code))
        restock(self.issue_storage, view_id, original_issue)
