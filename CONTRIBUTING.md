# Contributing to Scriba

Welcome to the repository of `scriba`! The following is a set of guidelines for contributing to Scriba.

#### Table Of Contents

[What should I know before I get started?](#what-should-i-know-before-i-get-started)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)

[Style Guides](#style-guides)
  * [Git Commit Messages](#git-commit-messages)
  * [Python Styleguide](#python-style-guide)
  * [Documentation Style Guide](#documentation-style-guide)

[Version Control](#version-control)

[Issue Labels](#issue-labels)

## What should I know before I get started?

### Learning Tools Interoperability (LTI)

LTI is a standard created by the IMS Global Learning Consortium that links content and resources to learning platforms (e.g. Canvas).

The documentation can be found here: https://www.imsglobal.org/activity/learning-tools-interoperability
Canvas also offers an introduction: https://canvas.instructure.com/doc/api/file.tools_intro.html

### Natural Language Toolkit

NLTK is a leading platform for building Python programs to work with human language data.
Check out the basics at https://www.nltk.org/

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for Scriba. Following these guidelines helps maintainers understand your report, reproduce the behavior, and find related reports.

Before creating bug reports, please check if it's already in the issues as you might find out that you don't need to create one. When you are creating a bug report, please [include as many details as possible](#how-do-i-submit-a-good-bug-report). Fill out [the required template](ISSUE_TEMPLATE.md), the information it asks for helps us resolve issues faster.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for Scriba, including completely new features and minor improvements to existing functionality. Following these guidelines helps maintainers and the community understand your suggestion and find related suggestions.

Before creating enhancement suggestions, please check if there is a related enhancement suggestion in the issues as you might find out that you don't need to create one. When you are creating an enhancement suggestion, please [include as many details as possible](#how-do-i-submit-a-good-enhancement-suggestion). Fill in [the template](ISSUE_TEMPLATE.md), including the steps that you imagine you would take if the feature you're requesting existed.

### Pull Requests

* Fill in [the required template](PULL_REQUEST_TEMPLATE.md)
* Do not include issue numbers in the PR title
* Include screenshots and animated GIFs in your pull request whenever possible.
* Follow the [Python](#python-style-guide) style guide.
* Include thoughtfully-worded, well-structured `unittest` tests in the `test.py` directories related to the appropriate feature. Run them using `python manage.py runserver`.
* Document new code based on the [Documentation Style Guide](#documentation-style-guide)
* End all files with a newline
* Avoid platform-dependent code
* Place imports in the following order:
    * Built in modules and packages (such as `os`)
    * Built in Scriba modules (such as `checker`)
    * Local modules (using relative paths)

## Style Guides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* When only changing documentation, include `[ci skip]` in the commit title
* Consider starting the commit message with an applicable emoji:
    * :art: `:art:` when improving the format/structure of the code
    * :racehorse: `:racehorse:` when improving performance
    * :memo: `:memo:` when writing docs
    * :bug: `:bug:` when fixing a bug
    * :fire: `:fire:` when removing code or files
    * :green_heart: `:green_heart:` when fixing the CI build
    * :white_check_mark: `:white_check_mark:` when adding tests
    * :lock: `:lock:` when dealing with security
    * :arrow_up: `:arrow_up:` when upgrading dependencies
    * :arrow_down: `:arrow_down:` when downgrading dependencies
    * :shirt: `:shirt:` when removing linter warnings

### Python Style Guide

The Python code follows [PEP 8](https://www.python.org/dev/peps/pep-0008/).

## Version Control

The following convention is used:

- `master`: the branch reflective production.
- `develop`: the branch for active development. Once a release is ready `develop` is merged into `master`.
- `feature/<issue number>/<description>`:
- `bug/<issue number>/<description>`:
- `task/<issue number>/<description>`:

### Managing Release Versions With Git Tags

In this model, a merge from develop to master is considered a new version release.
To track each release version, tags can be used.
These will be used as reference to choose which version should be deployed at the servers.

### Workflow

1. Move to `develop` branch: git checkout `develop`
2. Start a branch for a feature/bug/task `git checkout -b (feature|bug|task)/<issue number>/<description>`
3. Work on this newly created branch (commiting and pushing)
4. After finishing development on this task:
  - Go into GitHub and raise a pull request (Pull requests > New pull request)
  - The direction of the PR needs to be from your feature/bug/task branch to the develop branch
5. Wait for the developers on the team to approve the pull request, then merge the branches
6. When it is time for a new release do the same process, this time from `develop` to `master`.
7. Then create a tag announcing the release:
  - `git checkout master`
  - `git pull`
  - `git tag -a v1.0.0`
  - `git push origin v1.0.0 --follow-tags`

## Issue Labels

The labels are loosely grouped by their purpose, but it's not required that every issue have a label from every group or that an issue can't have more than one label from the same group.

### Type of Issue

| Label name | Description |
| --- | --- |
| `question` | General questions (e.g. how do I do X). |
| `story` | Functionality request expressed from the perspective of the user. |
| `bug` | Problem that impairs product or service functionality. |
| `task` | Task that needs to be done (e.g. refactoring, testing). |

### Topic Categories

| Label name | Description |
| --- | --- |
| `grammar` | Grammar related issue. |
| `semantics` | Semantics related issue. |
| `plagiarism` | Plagiarism related issue. |
| `academic-style` | Academic style related issue. |
| `citation` | Citation related issue. |
| `lti` | LTI related issue. |
