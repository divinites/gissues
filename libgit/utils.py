import sublime
import re
from .. import LINE_END
from .. import log, settings
from .. import COMMENT_START, COMMENT_END, ISSUE_START, ISSUE_END, HEADER_END, CONTENT_END, ADD_COMMENT, COMMENT_INFO
import os


def configure_issue_view(view):
    view.run_command("set_file_type", {"syntax": settings.get(
        "syntax", "Packages/Markdown/Markdown.sublime-syntax")})
    system_setting = view.settings()
    system_setting.set("wrap_width", settings.get("wrap_width", 0))
    system_setting.set("draw_centered", settings.get("draw_centered", False))
    custom_trigger = []
    commit_completion_trigger = settings.get("commit_completion_trigger",
                                             "&")[0]
    for char in ("@", "#", commit_completion_trigger):
        custom_trigger.append({"characters": char, "selector": "text.html"})
    auto_complete_trigger = system_setting.get("auto_complete_triggers")
    if auto_complete_trigger:
        for trigger in custom_trigger:
            if trigger not in auto_complete_trigger:
                auto_complete_trigger.append(trigger)
    else:
        auto_complete_trigger = custom_trigger
    system_setting.set("auto_complete_triggers", auto_complete_trigger)
    system_setting.set("issue_flag", True)
    view.set_scratch(True)


def print_list_framework(view=None):
    snippet = ''
    snippet += "=" * 50 + LINE_END
    snippet += 'Issue No.' + '   ' + 'Locked    ' + 'Issue Title' + LINE_END
    snippet += "=" * 24 + '**' + "=" * 24 + LINE_END
    snippet += "=" * 23 + "*" * 4 + "=" * 23 + LINE_END * 3
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
    view.settings().set('__vi_external_disable', settings.get('disable_vintageous') is True)
    return view


def find_list_region(view=None):
    view_converter = ViewConverter(view)
    _, start_point, end_point, _ = view_converter.find_region_line(
        "=" * 24 + '**' + "=" * 24, "=" * 23 + "*" * 4 + "=" * 23)
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
    snippet += "## Assignee     : " + str(issue['assignee']['login'] if issue[
        'assignee'] else str(None)) + LINE_END
    snippet += HEADER_END() + LINE_END
    snippet += ISSUE_START() + LINE_END
    snippet += filter_fake_crucial_lines(filter_line_ends(issue['body'])) + LINE_END
    snippet += ISSUE_END() + LINE_END
    log("Issue title " + issue["title"] + " formated")
    return snippet


def filter_fake_crucial_lines(content):
    robust_content = []
    for line in content.split(LINE_END):
        temp_line = line
        if line.startswith("*") or line.startswith("#"):
            for candidate in (COMMENT_START('')[:25],
                              COMMENT_END('')[:25],
                              ISSUE_START(),
                              ISSUE_END(),
                              HEADER_END(),
                              CONTENT_END(),
                              ADD_COMMENT()):
                if line.startswith(candidate):
                    temp_line = " " + line
        robust_content.append(temp_line)
    return LINE_END.join(robust_content)


def shape_comment(comment_info):
    wrap_width = settings.get("wrap_width", 0)
    if len(comment_info) >= wrap_width and wrap_width > 0:
        comment_info = comment_info[:78] + "*"
    return comment_info


def format_comment(comment):
    snippet = ''
    snippet += COMMENT_START(comment['id']) + LINE_END
    comment_info = COMMENT_INFO(comment['user']['login'], comment['updated_at'])
    snippet += shape_comment(comment_info) + LINE_END
    snippet += filter_fake_crucial_lines(filter_line_ends(comment['body'])) + LINE_END
    snippet += COMMENT_END(comment['id']) + LINE_END
    log("comment id " + str(comment['id']) + "formated")
    return snippet


def test_paths_for_executable(paths, test_file):
    for directory in paths:
        file_path = os.path.join(directory, test_file)
        if os.path.exists(file_path) and os.access(file_path, os.X_OK):
            return file_path

##
# @brief      find git function, thanks [sublime-github](https://github.com/bgreenlee/sublime-github)
##
# @return     the path of git
##


# def find_git():
#     git_path = settings.get("git_path", None)
#     if git_path:
#         return git_path
#     else:
#         path = os.environ.get('PATH', '').split(os.pathsep)
#         if os.name == 'nt':
#             git_cmd = 'git.exe'
#         else:
#             git_cmd = 'git'

#         git_path = test_paths_for_executable(path, git_cmd)
#         if not git_path:
#             if os.name == 'nt':
#                 extra_paths = (
#                     os.path.join(os.environ["ProgramFiles"], "Git", "bin"),
#                     os.path.join(os.environ["ProgramFiles(x86)"], "Git",
#                                  "bin"), )
#             else:
#                 extra_paths = ('/usr/local/bin',
#                                '/usr/local/git/bin', )
#             git_path = test_paths_for_executable(extra_paths, git_cmd)
#         return git_path


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
        for line, line_region in zip(self.readlines(),
                                     self.get_line_regions()):
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
        line_order = []
        for idx, line in enumerate(lines):
            if line.strip().startswith(HEADER_END()):
                line_order.append(CrucialLine("header_end", idx))
            elif line.strip().startswith(ISSUE_START()):
                line_order.append(CrucialLine("issue_start", idx))
            elif line.strip().startswith(ISSUE_END()):
                line_order.append(CrucialLine("issue_end", idx))
            elif re.match(r'^\*<+START\s+<Comment', line.strip()):
                line_order.append(
                    CrucialLine("comment_start", idx, int(
                        re.match(r"(\D+)(\d+)(.+)", line.strip()).group(2))))
            elif re.match(r'^\*>+END\s+<Comment', line.strip()):
                line_order.append(
                    CrucialLine("comment_end", idx, int(
                        re.match(r"(\D+)(\d+)(.+)", line.strip()).group(2))))
            elif line.strip().startswith(ADD_COMMENT()):
                line_order.append(CrucialLine("add_comment", idx))
            elif line.strip().startswith(CONTENT_END()):
                line_order.append(CrucialLine("content_end", idx))
            else:
                pass
        line_order.sort(key=lambda x: x.idx)
        view_lines_structure = LineLinkList()
        for line in line_order:
            view_lines_structure.add_node(line)
        while True:
            pointer = view_lines_structure.head
            before_purify = view_lines_structure.number
            while pointer:
                if not view_lines_structure.validate(pointer):
                    view_lines_structure.remove_node(pointer)
                pointer = pointer.next
            after_purify = view_lines_structure.number
            if before_purify == after_purify:
                break
        for crucial in ('issue_start', 'header_end', 'issue_end',
                        'comment_start', 'comment_end', 'add_comment',
                        'content_end'):
            crucial_line[crucial] = view_lines_structure.forward_search(
                view_lines_structure.head, crucial)
            log("the crucial_line[{}] is {}".format(crucial, repr(
                crucial_line[crucial])))
        duplicated = []
        for item in ('issue_start', 'header_end', 'issue_end', 'add_comment',
                     'content_end'):
            if len(crucial_line[item]) > 1:
                duplicated.append(item)
        if len(duplicated) > 0:
            raise Exception("mutilple possible crucial lines!")
        if len(crucial_line['comment_start']) != len(crucial_line[
                "comment_end"]):
            raise Exception("comment lines are not paired.")
        return crucial_line

    def select_true_crucials(self):
        pass

    @staticmethod
    def generate_issue_header(header):
        info_dict = {}
        for line in header:
            try:
                matched_item = re.search(r'(?<=#\s)(\w+)(\s+:\s*)(.*)', line)
                key = matched_item.group(1)
                value = matched_item.group(3)
                info_dict[key] = value
            except:
                pass
        log("issue_header is " + str(info_dict))
        return info_dict

    @staticmethod
    def get_issue_body(lines, crucial_lines):
        return '\n'.join(lines[crucial_lines['issue_start'][0].idx + 1:
                               crucial_lines['issue_end'][0].idx])
        # else:
        #     if len(crucial_lines['ADD_COMMENT()']) > 0:
        #         return '\n'.join(lines[crucial_lines['ISSUE_START()'][0].idx + 1:
        #                                crucial_lines['ADD_COMMENT()'][0].idx])
        #     else:
        #         return '\n'.join(lines[crucial_lines['ISSUE_START()'][0].idx + 1:
        #                                crucial_lines['ISSUE_END()'][0].idx])

    @staticmethod
    def get_comment_list(lines, crucial_lines):
        comment_dict = {}
        if len(crucial_lines['comment_start']) > 0:
            number_of_comments = len(crucial_lines['comment_start'])
            comment_pointer = 0
            while comment_pointer < number_of_comments:
                if crucial_lines['comment_start'][
                        comment_pointer].id != crucial_lines['comment_end'][
                            comment_pointer].id:
                    raise Exception(
                        "comment start and end numbers do not match")
                comment_headline_number = crucial_lines['comment_start'][
                    comment_pointer].idx
                comment_endline_number = crucial_lines['comment_end'][
                    comment_pointer].idx
                comment_id = crucial_lines['comment_start'][comment_pointer].id
                comment_body = '\n'.join(lines[comment_headline_number + 2:
                                               comment_endline_number])
                comment_dict[comment_id] = comment_body
                comment_pointer += 1
        return comment_dict

    @staticmethod
    def get_new_comment(lines, crucial_lines):
        if len(crucial_lines['add_comment']) > 0:
            return '\n'.join(lines[crucial_lines['add_comment'][0].idx + 1:
                                   crucial_lines['content_end'][0].idx]).strip()
        return ""


def get_issue_post(view):
    view_converter = ViewConverter(view)
    view_lines = view_converter.readlines()
    crucial_lines = ViewConverter.split_issue(view_lines)
    header = view_lines[:crucial_lines["header_end"][0].idx]
    issue_post = ViewConverter.generate_issue_header(header)
    issue_post = ViewConverter.prepare_post(issue_post)
    issue_post['body'] = ViewConverter.get_issue_body(view_lines,
                                                      crucial_lines)
    comment_dict = ViewConverter.get_comment_list(view_lines, crucial_lines)
    new_comment = ViewConverter.get_new_comment(view_lines, crucial_lines)
    log("new comment is {}".format(new_comment))
    return {'issue': issue_post,
            'label': issue_post.pop("label"),
            'comments': comment_dict,
            'new_comment': new_comment}


def find_comment_region(view):
    view_converter = ViewConverter(view)
    a, _, _, b = view_converter.find_region_line(ADD_COMMENT(), CONTENT_END())
    return (a, b)


def compare_issues(original_issue, issue_in_view):
    modified_keys = set(issue_in_view['issue'].keys())
    original_keys = set(original_issue['issue'].keys())
    intersection_keys = modified_keys.intersection(original_keys)
    log("intersection_keys are" + str(intersection_keys))
    modified_part = {
        key: issue_in_view['issue'][key]
        for key in intersection_keys
        if original_issue['issue'][key] != issue_in_view['issue'][key]
    }
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
        if issue_in_view['comments'][comment_id] != original_issue['comments'][
                comment_id]['body']:
            modified_comments[comment_id] = issue_in_view['comments'][
                comment_id]
    log("original_comments are " + str(original_issue["comments"]))
    log("modified_comments are " + str(modified_comments))
    return (modified_part, new_label, modified_comments, deleted_comments)


class CrucialLine:
    def __init__(self, line_type, idx, id=None):
        self.line_type = line_type
        self.idx = idx
        self.prev = None
        self.next = None
        self.id = id
        if not self.id:
            self.id = 0

    def __eq__(self, other):
        return self.idx == other.idx and self.line_type == other.line_type

    def __repr__(self):
        return "{} locates at {}".format(self.line_type, str(self.idx))


class LineLinkList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.number = 0

    def __repr__(self):
        pointer = self.head
        snip = 'head is {}'.format(repr(pointer))
        while pointer:
            snip += repr(pointer) + ', '
            pointer = pointer.next
        return snip

    def add_node(self, node):
        if self.number == 0:
            self.head = node
        if self.number == 1:
            self.tail = node
            self.head.next = self.tail
            self.tail.prev = self.head
        if self.number > 1:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.number += 1

    def remove_node(self, node):
        if self.head == node:
            self.head = self.head.next
            self.head.prev = None
        elif self.tail == node:
            self.tail = self.tail.prev
            self.tail.next = None
        else:
            left = node.prev
            right = node.next
            left.next = right
            right.prev = left
        self.number -= 1

    def validate(self, node):
        if node.line_type == 'header_end':
            if node.prev is None:
                return True
            else:
                return False
        if node.line_type == 'content_end':
            if node.next is None:
                return True
            else:
                return False
        if node.line_type == "issue_start":
            if node.prev.line_type != "header_end":
                return False
            return True
        if node.line_type == "issue_end":
            if node.next.line_type != "comment_start" and node.next.line_type != "add_comment" and node.next.line_type != "content_end":
                return False
            return True
        if node.line_type == "comment_start":
            if node.prev.line_type != "issue_end" and node.prev.line_type != "comment_end":
                return False
            return True
        if node.line_type == "comment_end":
            if node.next.line_type != "comment_start" and node.next.line_type != "add_comment":
                return False
            return True
        if node.line_type == "add_comment":
            if node.prev.line_type != "comment_end" and node.prev.line_type != "issue_end":
                return False
            return True

    def forward_search(self, start_point, node_type):
        pointer = start_point
        search_result = []
        while pointer:
            if pointer.line_type == node_type:
                search_result.append(pointer)
            pointer = pointer.next
        return search_result

    def backward_search(self, start_point, node_type):
        pointer = start_point
        search_result = []
        while pointer:
            if pointer.line_type == node_type:
                search_result.append(pointer)
            pointer = pointer.prev
        return search_result
