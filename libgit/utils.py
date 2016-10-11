import sublime
import re
# from .. import parameter_container as pc
from .. import LINE_END
from .. import log, settings


def configure_view_trigger(view):
    if view.settings().get('syntax') == settings.get("syntax", "Packages/GitHubIssue/Issue.sublime-syntax"):
        system_setting = view.settings()
        custom_trigger = []
        commit_completion_trigger = settings.get("commit_completion_trigger", "&")[0]
        # for comletion_scope in COMPLETIONS_SCOPES:
        #     for char in ("@", "#", commit_completion_trigger):
        #         custom_trigger.append({"characters": char, "selector": comletion_scope})
        for char in ("@", "#", commit_completion_trigger):
            custom_trigger.append({"characters": char, "selector": "text"})
        auto_complete_trigger = system_setting.get("auto_complete_triggers")
        if auto_complete_trigger:
            for trigger in custom_trigger:
                if trigger not in auto_complete_trigger:
                    auto_complete_trigger.append(trigger)
        else:
            auto_complete_trigger = custom_trigger
        system_setting.set("auto_complete_triggers", auto_complete_trigger)
        system_setting.set("issue_flag", True)


def print_list_framework(view=None):
    snippet = ''
    snippet += "-" * 50 + LINE_END
    snippet += 'Issue No.' + '   ' + 'Locked    ' + 'Issue Title' + LINE_END
    snippet += "-" * 24 + '**' + "-" * 24 + LINE_END
    snippet += "-" * 23 + "*" * 4 + "-" * 23 + LINE_END * 3
    snippet += "Page:  |_First_|     ...     |_Prev_|     ...     |_Next_|     ...     |_Last_|" + LINE_END
    if not view:
        view = sublime.active_window().new_file()
    view.run_command("erase_snippet")
    view.run_command("set_file_type",
                     {"syntax":
                      "Packages/GitHubIssue/list.sublime-syntax"})
    view.settings().set('color_scheme',
                        "Packages/GitHubIssue/list.hidden-tmTheme")
    view.run_command("insert_issue_snippet", {"snippet": snippet})
    view.set_scratch(True)
    view.set_read_only(True)
    view.settings().set("list_flag", True)
    return view


def find_list_region(view=None):
    view_converter = ViewConverter(view)
    _, start_point, end_point, _ = view_converter.find_region_line(
        "-" * 24 + '**' + "-" * 24, "-" * 23 + "*" * 4 + "-" * 23)
    return (start_point, end_point)


def restock(storage, key, item):
    if not storage.empty():
        dictionary = storage.get()
        dictionary[key] = item
        storage.put(dictionary)


def show_stock(storage, key):
    if not storage.empty():
        dictionary = storage.get()
        content = dictionary[key]
        storage.put(dictionary)
        return content


def destock(storage, key):
    if not storage.empty():
        dictionary = storage.get()
        try:
            del dictionary[key]
        except:
            pass
        storage.put(dictionary)


def format_issue(issue):
    labels = []
    if issue["labels"]:
        for label_obj in issue["labels"]:
            labels.append(label_obj['name'])
    snippet = ''
    snippet += "# Title         : " + issue["title"] + LINE_END
    snippet += "## Number       : " + str(issue['number']) + LINE_END
    snippet += "## State        : " + issue['state'] + LINE_END
    snippet += "## Label        : " + \
        " ".join(['@' + label for label in labels]) + LINE_END
    snippet += "## Locked       : " + str(issue['locked']) + LINE_END
    snippet += "## Assignee     : " + str(issue['assignee']) + LINE_END
    snippet += "*" + '-' * 10 + "Content" + '-' * 10 + "*" + LINE_END
    snippet += filter_line_ends(issue['body']) + LINE_END
    log("Issue title " + issue["title"] + " formated")
    return snippet


def format_comment(comment):
    snippet = ''
    snippet += "*" + '-' * 10 + "Start <Comment " + \
        str(comment['id']) + '>' + '-' * 10 + "*" + LINE_END
    snippet += "*<commented by " + comment['user'][
        'login'] + "   UpdateTime: " + comment[
            'updated_at'] + '>*' + LINE_END
    snippet += filter_line_ends(comment['body']) + LINE_END
    snippet += "*" + '-' * 10 + "End <Comment " + \
        str(comment['id']) + '>' + '-' * 10 + "*" + LINE_END
    log("comment id " + str(comment['id']) + "formated")
    return snippet


def find_git():
    git_path = settings.get("git_path", '')
    if settings.get("git_path", ''):
        return git_path
    if sublime.platform() != 'windows':
        log('using git')
        return 'git'
    else:
        log('using git.exe')
        return 'git.exe'


def filter_line_ends(issue):
    # if LINE_END == '\n':
    log("filtering line ends")
    return issue.replace('\r', '')
    # else:
    #     log("no need to fix issue line ends")
    #     return issue


class ViewConverter:

    def __init__(self, view):
        self.view = view

    @staticmethod
    def prepare_post(info_dict):
        prepared_dict = {}
        for key, value in info_dict.items():
            prepared_key = key.lower()
            if value == 'False':
                log(str(key) + " value is " + value)
                prepared_value = False
            elif value == 'True':
                log(str(key) + " value is " + value)
                prepared_value = True
            elif value == 'None':
                log(str(key) + " value is " + value)
                prepared_value = None
            elif value.isdigit():
                log(str(key) + " value is " + value)
                prepared_value = int(value)
            elif prepared_key == 'label':
                log(str(key) + " value is " + value)
                prepared_value = set([x.strip() for x in value.split('@')])
                log("prepared value is {}".format(str(prepared_value)))
                try:
                    prepared_value.remove('')
                except KeyError:
                    pass
                log("labels are " + str(prepared_value))
            else:
                prepared_value = value
            prepared_dict[prepared_key] = prepared_value
        return prepared_dict

    def find_region_line(self, region_start_string, region_end_string):
        a, b, c, d = 0, 0, 0, 0
        for line, line_region in zip(self.readlines(), self.get_line_regions()):
            if line.strip().startswith(region_start_string):
                a = line_region.a
                c = line_region.b
            if line.strip().startswith(region_end_string):
                b = line_region.b
                d = line_region.a
        return (a, c, d, b)

    def readlines(self):
        lines = []
        line_regions = self.get_line_regions()
        for region in line_regions:
            lines.append(self.view.substr(region))
        return lines

    def get_line_regions(self):
        return self.view.lines(sublime.Region(0, self.view.size()))

    @staticmethod
    def split_issue(lines):
        crucial_line = {}
        crucial_line['header_end'] = 0
        crucial_line['comment_start'] = []
        crucial_line['comment_end'] = []
        crucial_line['add_comment'] = 0
        crucial_line['end'] = 0
        for idx, line in enumerate(lines):
            if line.strip().startswith("*" + "-" * 10 + "Content"):
                crucial_line["header_end"] = idx
            elif line.strip().startswith("*" + '-' * 10 + "Start <Comment"):
                crucial_line["comment_start"].append(idx)
            elif line.strip().startswith("*" + '-' * 10 + "End <Comment"):
                crucial_line["comment_end"].append(idx)
            elif line.strip().startswith("## Add New Comment:"):
                crucial_line["add_comment"] = idx
            elif line.strip().startswith("*" + "-" * 10 + "END"):
                crucial_line["end"] = idx
            else:
                pass
        log("curcial line is " + str(crucial_line))
        return crucial_line

    @staticmethod
    def generate_issue_header(header):
        info_dict = {}
        for line in header:
            matched_item = re.search(r'(?<=#\s)(\w+)(\s+:\s*)(.*)', line)
            key = matched_item.group(1)
            value = matched_item.group(3)
            info_dict[key] = value
        log("issue_header is " + str(info_dict))
        return info_dict

    @staticmethod
    def get_issue_body(lines, crucial_lines):
        if crucial_lines['comment_start']:
            return '\n'.join(lines[crucial_lines['header_end'] + 1:
                                   crucial_lines['comment_start'][0]])
        else:
            if crucial_lines['add_comment']:
                return '\n'.join(lines[crucial_lines['header_end'] + 1:
                                       crucial_lines['add_comment']])
            else:
                return '\n'.join(lines[crucial_lines['header_end'] + 1:crucial_lines['end']])

    @staticmethod
    def get_comment_list(lines, crucial_lines):
        comment_dict = {}
        if crucial_lines['comment_start']:
            number_of_comments = len(crucial_lines['comment_start'])
            comment_pointer = 0
            while comment_pointer < number_of_comments:
                comment_headline_number = crucial_lines['comment_start'][
                    comment_pointer]
                comment_endline_number = crucial_lines[
                    'comment_end'][comment_pointer]
                comment_id = int(re.search(r'(?<=\<Comment\s).*(?=>)', lines[
                    comment_headline_number]).group(0).strip())
                comment_body = '\n'.join(lines[comment_headline_number + 2:
                                               comment_endline_number])
                comment_dict[comment_id] = comment_body
                comment_pointer += 1
        return comment_dict

    @staticmethod
    def get_new_comment(lines, crucial_lines):
        return '\n'.join(lines[crucial_lines['add_comment'] + 1: crucial_lines['end']]).strip()


def get_issue_post(view):
    view_converter = ViewConverter(view)
    view_lines = view_converter.readlines()
    crucial_lines = ViewConverter.split_issue(view_lines)
    header = view_lines[:crucial_lines["header_end"]]
    issue_post = ViewConverter.generate_issue_header(header)
    issue_post = ViewConverter.prepare_post(issue_post)
    issue_post['body'] = ViewConverter.get_issue_body(view_lines,
                                                      crucial_lines)
    comment_dict = ViewConverter.get_comment_list(view_lines, crucial_lines)
    new_comment = ViewConverter.get_new_comment(view_lines, crucial_lines)
    return {'issue': issue_post,
            'label': issue_post.pop("label"),
            'comments': comment_dict,
            'new_comment': new_comment}


def find_comment_region(view):
    view_converter = ViewConverter(view)
    a, _, _, b = view_converter.find_region_line(
        "## Add New Comment:", "*" + "-" * 10 + "END")
    return (a, b)


def compare_issues(original_issue, issue_in_view):
    modified_keys = set(issue_in_view['issue'].keys())
    original_keys = set(original_issue['issue'].keys())
    intersection_keys = modified_keys.intersection(original_keys)
    log("intersection_keys are" + str(intersection_keys))
    modified_part = {key: issue_in_view['issue'][key]
                     for key in intersection_keys
                     if original_issue['issue'][key] != issue_in_view[
                         'issue'][key]}
    additional_keys = modified_keys.difference(original_keys)
    if additional_keys:
        additional_part = {key: issue_in_view['issue'][key]
                           for key in additional_keys}
        modified_part.update(additional_part)
    log('original_issue is' + str(original_issue['issue']))
    log("modified_parts are " + str(modified_part))
    new_label = -1
    if original_issue['label'] != issue_in_view['label']:
        new_label = issue_in_view['label']
    modified_comments = {}
    comment_ids_in_view = set(issue_in_view['comments'].keys())
    original_comment_ids = set(original_issue['comments'].keys())
    deleted_comments = original_comment_ids.difference(comment_ids_in_view)
    for comment_id in issue_in_view['comments'].keys():
        if issue_in_view['comments'][comment_id] != original_issue['comments'][comment_id]['body']:
            modified_comments[comment_id] = issue_in_view[
                'comments'][comment_id]
    log("original_comments are " + str(original_issue["comments"]))
    log("modified_comments are " + str(modified_comments))
    return (modified_part, new_label, modified_comments, deleted_comments)
