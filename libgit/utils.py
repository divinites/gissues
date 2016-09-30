import sublime
import re
import logging

LINE_ENDS = '\n' if sublime.platform() != 'windows' else '\r\n'
DEBUG_FLAG = sublime.load_settings("github_issue.sublime-settings").get('debug', 0)


def format_issue(issue):
    snippet = ''
    snippet += "# Title         : " + issue["title"] + LINE_ENDS
    snippet += "## Number       : " + str(issue['number']) + LINE_ENDS
    snippet += "## State        : " + issue['state'] + LINE_ENDS
    snippet += "## Locked       : " + str(issue['locked']) + LINE_ENDS
    snippet += "## Assignee     : " + str(issue['assignee']) + LINE_ENDS
    snippet += "*" + '-' * 10 + "Content" + '-' * 10 + "*" + LINE_ENDS
    snippet += filter_line_ends(issue['body']) + LINE_ENDS
    return snippet


def format_comment(comment):
    snippet = ''
    snippet += "*" + '-' * 10 + "Start <Comment " + str(comment['id']) + '>' + '-' * 10 + "*" + LINE_ENDS
    snippet += "*<commented by " + comment['user'][
        'login'] + "   UpdateTime: " + comment[
            'updated_at'] + '>*' + LINE_ENDS
    snippet += filter_line_ends(comment['body']) + LINE_ENDS
    snippet += "*" + '-' * 10 + "End <Comment " + str(comment['id']) + '>' + '-' * 10 + "*" + LINE_ENDS
    return snippet


def find_git():
    if sublime.platform() != 'windows':
        logging.debug('using git')
        return 'git'
    else:
        logging.debug('using git.exe')
        return 'git.exe'


def filter_line_ends(issue):
    if sublime.platform() != 'windows':
        return issue.replace('\r', '')
    else:
        return issue


class ViewConverter:
    def __init__(self, view):
        self.view = view

    @staticmethod
    def prepare_post(info_dict):
        prepared_dict = {}
        for key, value in info_dict.items():
            prepared_key = key.lower()
            if value == 'False':
                logging.debug(str(key) + "value is " + value)
                prepared_value = False
            elif value == 'True':
                logging.debug(str(key) + "value is " + value)
                prepared_value = True
            elif value == 'None':
                logging.debug(str(key) + "value is " + value)
                prepared_value = None
            elif value.isdigit():
                logging.debug(str(key) + "value is " + value)
                prepared_value = int(value)
            else:
                prepared_value = value
                logging.debug(str(key) + "value is " + value)
            prepared_dict[prepared_key] = prepared_value
        return prepared_dict

    def find_region(self, region_start_string, region_end_string):
        a, b = 0, 0
        for line, line_region in zip(self.readlines(), self.get_line_regions()):
            if line.strip().startswith(region_start_string):
                a = line_region.a
            if line.strip().startswith(region_end_string):
                b = line_region.b
        return (a, b)

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
        logging.debug("curcial line is " + str(crucial_line))
        return crucial_line

    @staticmethod
    def generate_issue_header(header):
        info_dict = {}
        for line in header:
            matched_item = re.search(r'(?<=#\s)(\w+)(\s+:\s*)(.*)', line)
            key = matched_item.group(1)
            value = matched_item.group(3)
            info_dict[key] = value
        logging.debug("issue_header is " + str(info_dict))
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
                comment_endline_number = crucial_lines['comment_end'][comment_pointer]
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
            'comments': comment_dict,
            'new_comment': new_comment}


def create_new_issue_view():
    snippet = ''
    snippet += "# Title         : " + LINE_ENDS
    snippet += "## Assignee     : " + LINE_ENDS
    snippet += "*" + '-' * 10 + "Content" + '-' * 10 + "*" + LINE_ENDS
    snippet += LINE_ENDS
    snippet += "*" + '-' * 10 + "END" + '-' * 10 + "*" + LINE_ENDS
    view = sublime.active_window().new_file()
    view.run_command("set_file_type",
                      {"syntax":
                       "Packages/GitHubIssue/issue.tmLanguage"})
    view.run_command("insert_issue", {"issue": snippet})
    view.set_scratch(True)


def find_comment_region(view):
    view_converter = ViewConverter(view)
    return view_converter.find_region("## Add New Comment:", "*" + "-" * 10 + "END")


def compare_issues(original_issue, issue_in_view):
    modified_keys = set(issue_in_view['issue'].keys())
    original_keys = set(original_issue['issue'].keys())
    intersection_keys = modified_keys.intersection(original_keys)
    logging.debug("intersection_keys are" + str(intersection_keys))
    modified_part = {key: issue_in_view['issue'][key]
                     for key in intersection_keys
                     if original_issue['issue'][key] != issue_in_view[
                         'issue'][key]}
    additional_keys = modified_keys.difference(original_keys)
    if additional_keys:
        additional_part = {key: issue_in_view['issue'][key]
                           for key in additional_keys}
        modified_part.update(additional_part)
    logging.debug('original_issue is' + str(original_issue['issue']))
    logging.debug("modified_parts are " + str(modified_part))
    modified_comments = {}
    comment_ids_in_view = set(issue_in_view['comments'].keys())
    original_comment_ids = set(original_issue['comments'].keys())
    deleted_comments = original_comment_ids.difference(comment_ids_in_view)
    for comment_id in issue_in_view['comments'].keys():
        if issue_in_view['comments'][comment_id] != original_issue['comments'][comment_id]['body']:
            modified_comments[comment_id] = issue_in_view['comments'][comment_id]
    logging.debug("original_comments are " + str(original_issue["comments"]))
    logging.debug("modified_comments are " + str(modified_comments))
    return (modified_part, modified_comments, deleted_comments)
