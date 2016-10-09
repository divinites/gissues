# GitHub-Issues

## Introduction

This plugin aims at providing a convenient way to write and update issues inside sublime text. Instead of opening a external Internet browser, this plug-in open a new buffer and let users to write/modify issue content using Markdown natively within sublime Text.

It was initially inspired by github-issues.vim.

## Features

- Create/post/update/open/close github issues inside Sublime Text.

- Browse/navigate the issue list of any public repos and users' private repos.

- Auto-complete issue titles, labels and issue participants.

- Using Markdown as the default syntax of issue, allowing users to choose other syntaxes as well.


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
    "syntax": "Packages/GitHubIssue/Issue.sublime-syntax",
    "git_path": "",
    "issue\_title\_completion": true,
    "user_completion": true,
    "label_completion": true,
    "custom\_completion\_scope": []

}
```

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

*"debug"* is a flag, if it is set to 1, the plug-in will print every single step and output in sublime console. Normally it should be set to 0.

*"syntax"* is your preferred markdown syntax for issue view.

_"git\_path"_ is where your git executable lies, if git is in your system path, you normally do not need to set it.
_"issue\_title\_completion"_, _"user\_completion"_ and _"label\_completion"_ are autocompletion flags:

- _"issue\_title\_completion"_ autocompletes other issue titles, so that users can easily refer them;

- _"user\_completion"_ autocompletes issue participants, so that users can easily _@_ them;

- _"label\_completion"_ autocompletes labels (only available in the "##Label     :" line).

_"custom\_completion\_scope"_: By default, autocompletion only takes place in the scope "text.html.github.issue", if you have customized syntax, you probably want to add correponding scopes here to make autocompletion work under your syntax.

After installing this plug-in, it would be better to restart sublime text to make the plug-in work.

## Usage

All commands are runnable through Command Palette, please have a look at *Command Palette.sublime-commands* and type _GithubIssue_ to get more ideas about the commands available.

Some shortcut keys are pre-defined:

- In an issue List view, Press **Enter** to open a particular issue, Press **Right/Left Arrow** turn to issue page down/up.

- In an issue List view, Press **Ctrl + Right/Left Arrow** to goto last/first page of issues.

- In an issue view, Press **Super+S**(**Ctrl+S** in Windows)to sync current issue or comments with Github

- in an issue view, you can **open**, **close**, __lock__ or __unlock__ an issue simply by changing corresponding line.


## Illustration

- Show issue list:
![show issue list](https://www.scislab.com/static/media/uploads/blog/open_list.gif)

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

## Change Log

- 0.0.1: First public version, only show list works.

- 0.1.0: All basic function works.

- 1.0.0: Add messages, dependencies and ready for Package Control Channel.

- 1.1.0: Add the feature that users can directly enter repo information and write issues/comments.

- 1.2.0: Add logging system and solve CRLF problems.

- 1.3.0: Add issue syntax customization and adjust cursor position.

- 1.5.0: Add issue list pagination and page view control

- 1.6.0: Add basic label support

- 2.0.0: Add auto-completion support

- 2.1.0: Add protection to the issue header and add a command "post_or_update_issue"

- 2.1.6: various minor improvements


