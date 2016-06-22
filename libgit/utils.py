import sublime
import re


LINE_ENDS = '\n' if sublime.platform() != 'windows' else '\r\n'


def log():
    pass


def find_git():
    if sublime.platform() != 'windows':
        return 'git'
    else:
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
                prepared_value = False
            elif value == 'True':
                prepared_value = True
            elif value == 'None':
                prepared_value = None
            elif value.isdigit():
                prepared_value = int(value)
            else:
                prepared_value = value
            prepared_dict[prepared_key] = prepared_value
        return prepared_dict

    def readlines(self):
        lines = []
        line_regions = self.view.lines(sublime.Region(0, self.view.size()))
        for region in line_regions:
            lines.append(self.view.substr(region))
        return lines

    @staticmethod
    def split_issue(lines):
        crucial_line = {}
        crucial_line['header_end'] = 0
        crucial_line['comment_start'] = []
        crucial_line['add_comment'] = 0
        for idx, line in enumerate(lines):
            if line.startswith("## Content      :"):
                crucial_line["header_end"] = idx
            elif line.startswith("## Comment ID:"):
                crucial_line["comment_start"].append(idx)
            elif line.startswith("## Add New Comment:"):
                crucial_line["add_comment"] = idx
                break
            else:
                pass
        return crucial_line

    @staticmethod
    def generate_issue_header(header):
        info_dict = {}
        for line in header:
            matched_item = re.search(r'(?<=#\s)(\w+)(\s+:\s*)(.*)', line)
            key = matched_item.group(1)
            value = matched_item.group(3)
            info_dict[key] = value
        return info_dict

    @staticmethod
    def get_issue_body(lines, crucial_lines):
        if crucial_lines['comment_start']:
            return '\n'.join(lines[crucial_lines['header_end'] + 2: crucial_lines['comment_start'][0]])
        else:
            if crucial_lines['add_comment']:
                return '\n'.join(lines[crucial_lines['header_end'] + 2: crucial_lines['add_comment']])
            else:
                return '\n'.join(lines[crucial_lines['header_end'] + 2:])

    @staticmethod
    def get_comment_list(lines, crucial_lines):
        comments = []
        comment_id_list = []
        if crucial_lines['comment_start']:
            number_of_comments = len(crucial_lines['comment_start'])
            comment_pointer = 0
            while comment_pointer < number_of_comments:
                comment_headline_number = crucial_lines['comment_start'][comment_pointer]
                if comment_pointer + 1 < number_of_comments:
                    next_headline_number = crucial_lines['comment_start'][comment_pointer + 1]
                else:
                    next_headline_number = crucial_lines['add_comment']
                comment_id_list.append(int(re.search('(?<=Comment ID:).*', lines[comment_headline_number]).group(0).strip()))
                comments.append('\n'.join(lines[comment_headline_number + 2: next_headline_number]))
                comment_pointer += 1
            return (comment_id_list, comments)
        else:
            return ([], [])

    @staticmethod
    def get_new_comment(lines, crucial_lines):
        return '\n'.join(lines[crucial_lines['add_comment'] + 1:])


def create_new_issue_view():
    snippet = ''
    snippet += "# Title         : " + LINE_ENDS
    snippet += "## Assignee     : " + LINE_ENDS
    snippet += "## Content      : " + LINE_ENDS
    snippet += LINE_ENDS
    view = sublime.active_window().new_file()
    view.set_syntax_file(
        'Packages/Markdown Extended/Syntaxes/Markdown Extended.sublime-syntax')
    # view.settings.set('color_scheme', 'Packages/MarkdownEditing/Markdown.tmLanguage')
    view.run_command("set_file_type", {"syntax": "Packages/MarkdownEditing/Markdown.tmLanguage"})
    view.run_command("insert_issue", {"issue": snippet})
    view.set_scratch(True)
