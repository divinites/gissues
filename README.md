# GitHub-Issues

## Introduction

This plugin aims at providing a convenient way to write and update issues inside sublime text. Instead of opening a external Internet browser, this plug-in open a new buffer and let users to write/modify issue content using Markdown natively within sublime Text.

It was initially inspired by github-issues.vim.


## Configuration

Set-ups:

- Open Preferences -> Package Settings -> Github Issue
- Open Settings - User
- There is a sample configuration in Settings - Default
- Four options available:

```json
{
"token": "",
"username": "",
"password": "",
"debug": 0
 }
```

Token means the github access token, you can get one from [this link](https://github.com/settings/tokens)

Alternatively, you can use password (not recommended, since username and password will be stored in the configuration file in plain text). The program will first look at whether token is set, if no token, it will then look at pasword option.

To sum up, the username is always required, passowrd and token are optional but at least one of them should be provided.

debug is a flag, if it is set to 1, the plug-in will print every single step and output in sublime console. Normally it should be set to 0.

After installing this plug-in, it would be better to restart sublime text to make the plug-in work.

## Usage

All commands are runnable through Command Palette, please have a look at *Command Palette.sublime-commands* to get more ideas about the commands available.

Some shortcut keys are pre-defined:

- In an issue List view, Press **Enter** or **Right Arrow** to open a particular issue
- In an issue view, Press **Super+S** to sync current issue or comments with Github
- In an issue view, Press **Super+Shift+S** to post a new issue to Github


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




