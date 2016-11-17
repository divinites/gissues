# GitHub-Issues

## Introduction

This plugin aims at providing a convenient way to write and update issues inside sublime text. Instead of opening a external Internet browser, this plug-in open a new buffer and let users to write/modify issue content using Markdown natively within sublime Text.

It was initially inspired by github-issues.vim.

## Features

- Create/post/update/open/close github issues inside Sublime Text.

- Browse/navigate the issue list of any public repos and users' private repos.

- Auto-complete issue titles, labels and issue participants.

- Using Markdown as the default syntax of issue, allowing users to choose other syntaxes as well.

## Installation

Search **GitHubIssue** in Package Control Channel. After installation, you will need to restart Sublime Text.


## Configuration

Set-ups:

- Open Preferences -> Package Settings -> Github Issue

- Open Settings - User

- There is a sample configuration in Settings - Default

- Ten options available:

```json
{
    "token": "",
    "username": "",
    "password": "",
    "debug": 0,
    "syntax": "Packages/Markdown/Markdown.sublime-syntax",
    "wrap_width": 80,
    "draw_centered": true,
    "split_line_width": 0,
    "issue_title_completion": true,
    "user_completion": true,
    "label_completion": true,
    "commit_completion": true,
    "commit_completion_trigger": "&"
    "disable_vintageous": true
}
```
### Authentication:
Token means the github access token, you can get one from [this link](https://github.com/settings/tokens)

**Attention! To have a usable token, it would be safe to choose the following scopes when generating the token:**

- _admin:org_,

- _admin:org\_hook_,

- _admin:public\_key_,

- _admin:repo\_hook_,

- _gist_,

- _notifications_,

- _repo_

If you find without one or more scopes listed above, the plug-in also works properly, please submit an issue. After testing, I will modify the scope list.

Alternatively, you can use password (not recommended, since username and password will be stored in the configuration file in plain text). The program will first look at whether token is set, if no token, it will then look at pasword option.

To sum up, the username is always required, passowrd and token are optional but at least one of them should be provided.

### Customisation

- **"syntax"** is your preferred markdown syntax for issue view.

- **"wrap_width"** is the same as "wrap_width" in preference.sublime-settings, but limited to issue views, default value 80.

- **"draw_centered"** is the same as "draw_centered" in preferences.sublime-settings, also limited to issue view, default value: **False**.

-**"split_line_width"** is the width of split lines. default value is  0, which means that it will be the same as wrap_width.

### Auto-Completion

GitHubIssue offers a range of auto-completion options:

- __"issue\_title\_completion"__, __"user\_completion"__ and __"label\_completion"__ are autocompletion flags:

- __"issue\_title\_completion"__ autocompletes other issue titles, so that users can easily refer them;

- __"user\_completion"__ autocompletes issue participants, so that users can easily __@__ them;

- __"label\_completion"__ autocompletes labels (only available in the "##Label     :" line, triggered by __@__).

- __"commit\_completion"__: you type commitment messages, auto-completes commit SHA. default "true".

- __"commit\_completion\_trigger"__: the trigger for commit auto-completion, default value "&".


### Miscellaneous

- **"debug"** is a flag, if it is set to 1, the plug-in will print every single step and output in sublime console. Normally it should be set to 0.

-__"disable\_local\_repositories"__: normally, GitHub Issue will use git command to automatically discover github repos on the side-bar. If you do not want GitHub Issue to do so, please sent this flag to **true**. Default value is **false**.

- **"disable_vintageous"**: if this is set true, issue list will also be shown in normal mode.


After installing this plug-in, it would be better to restart sublime text to make the plug-in work.

## Commands and Shortcuts

### Commands

All commands are runnable through Command Palette, please have a look at *Command Palette.sublime-commands* and type _GithubIssue_ to get more ideas about the commands available.

```json
[
    {
        "caption": "GitHub Issue: Show Open Issues",
        "args": {"per_page": 30},
        "command": "show_github_issue_list"
    },
    {
        "caption": "GitHub Issue: Show All Issues",
        "args": {"state": "all", "per_page": 30},
        "command": "show_github_issue_list"
    },
    {
        "caption": "GitHub Issue: Show Issue",
        "args": {},
        "command": "show_github_issue"
    },
    {
        "caption": "GitHub Issue: Create Issue",
        "args": {},
        "command": "new_github_issue"
    },
    {
        "caption": "GitHub Issue: post/update Issue",
        "args": {},
        "command": "post_or_update_issue"
    },
    {
        "caption": "GitHub Issue: close/reopen Issue",
        "args": {},
        "command": "update_and_close_or_reopen_issue"
    },
]
```

### Shortcuts

You can define your own shortcut, but some shortcut keys are pre-defined for your convenience.

- In an issue List view, Press <kbd>Enter</kbd> to open a particular issue, Press <kbd>Right/Left Arrow</kbd> turn to issue page down/up.

- In an issue List view, Press <kbd>Ctrl + Right/Left Arrow</kbd> to goto last/first page of issues.

- In an issue List view, Press <kbd>Ctrl + r</kbd> to refresh open issue list, <kbd>Ctrl + Shift + r</kbd> to refresh all issue list.

- In an issue view, Press <kbd>Super+S</kbd>(<kbd>Ctrl+S</kbd> in Windows)to sync current issue or comments with Github

- in an issue view, you can press <kbd>Ctrl + shift + u</kbd> to toggle open/close an issue.


## Illustration

- Show issue list:
![show issue list](https://www.scislab.com/static/media/uploads/PrivateGraphs/showlist.gif)

- Create an Issue:
![create an issue](https://www.scislab.com/static/media/uploads/blog/create_issue.gif)


- Update an Issue:
![update an issue](https://www.scislab.com/static/media/uploads/blog/update_issue.gif)


- Add a comment:
![add a comment](https://www.scislab.com/static/media/uploads/blog/add_comment.gif)

- Delete a comment:
![delete a comment](https://www.scislab.com/static/media/uploads/blog/delete_comment.gif)

- Modify a comment:
![modify a comment](https://www.scislab.com/static/media/uploads/blog/modi_comment.gif)

- Auto-completion of labels, if a label does not exist, it will be automatically created.
![label completion](https://www.scislab.com/static/media/uploads/PrivateGraphs/label.gif)

- Auto-Completion of commits, issue references and other participants.
![auto-completion](https://www.scislab.com/static/media/uploads/PrivateGraphs/completion.gif)


## Change Log

- **0.0.1**: First public version, only show list works.

- **0.1.0**: All basic function works.

- **1.0.0**: Add messages, dependencies and ready for Package Control Channel.

- **1.1.0**: Add the feature that users can directly enter repo information and write issues/comments.

- **1.2.0**: Add logging system and solve CRLF problems.

- **1.3.0**: Add issue syntax customization and adjust cursor position.

- **1.5.0**: Add issue list pagination and page view control

- **1.6.0**: Add basic label support

- **2.0.0**: Add auto-completion support

- **2.1.0**: Add protection to the issue header and add a command "post_or_update_issue"

- **2.2.0**: various minor improvements

- **2.3.0**: Add commit auto-completion

- **2.5.0**: Refactoring

- **2.6.0**: Add a linklist structure to issue view, add refresh list option, reformat issue and comment header lines.


