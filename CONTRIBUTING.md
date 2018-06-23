# Contributing to Scriba

Welcome to the repository of `scriba`! The following is a set of guidelines for contributing to Scriba.

#### Table Of Contents

[What should I know before I get started?](#what-should-i-know-before-i-get-started)

[How Can I Contribute?](#how-can-i-contribute)
  * [Reporting Bugs](#reporting-bugs)
  * [Suggesting Enhancements](#suggesting-enhancements)
  * [Your First Code Contribution](#your-first-code-contribution)
  * [Pull Requests](#pull-requests)

[Styleguides](#styleguides)
  * [Git Commit Messages](#git-commit-messages)
  * [JavaScript Styleguide](#javascript-styleguide)
  * [CoffeeScript Styleguide](#coffeescript-styleguide)
  * [Specs Styleguide](#specs-styleguide)
  * [Documentation Styleguide](#documentation-styleguide)

[Additional Notes](#additional-notes)
  * [Issue and Pull Request Labels](#issue-and-pull-request-labels)

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

## Style guides

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

### Documentation Style Guide

## Additional Notes

### Version Control

The repository uses the [Feature Branch Model](https://hackernoon.com/still-using-gitflow-what-about-a-simpler-alternative-74aa9a46b9a3).

#### Worflow

1. Create a branch from the master (feature-x), which is where the feature will be developed: `git checkout -b feature-x`
2. Push the branch to the remote: `git push -u origin feature-x`. With the branch in the remote repo, a pull request should be opened with it.
3. Fix the reviewed code and wait for approval. If a new release on the master generates a conflict, a best practice would be to rebase it (instead of merging).
4. (optional) If a rebase is needed: checkout to master `git checkout master`, pull the changes `git pull`, go back to the feature branch `git checkout feature-x`, do the rebase `git rebase master` and then sync the rebased branch `git push --force-with-lease`.
5. If there are no conflicts and it was approved: `git checkout master` then `git merge --squash feature-x` then `git commit`.

#### Managing Release Versions With Git Tags

In the feature branch model, a merge is considered a new version release. To track each release version, tags can be used. These will be used as reference to choose which version should be deployed at the servers.

The process is:

1. Checkout to the master branch: `git checkout master`
2. Pull changes from the remote `git pull`
3. Create a tag using `git tag -a v1.0.0`
4. Push the modifications and the tag: `git push origin v1.0.0 --follow-tags`

#### What happens if a hot-fix is needed?

At some point, an issue will be raised and the production version will need a hot-fix. A feature branch can't just be opened to develop a fix, as the master will probably be ahead of the production version. In this case, the fix needs to be done directly on the production version:

1. Checkout to the production version tag `git checkout v0.10.0`.
2. Create a new branch from this tag `git checkout -b hotfix-v0.10.1-weirdbehavior`.
3. Create the fix and commit it.
4. Create a tag for this new release `git tag -a v0.10.1`.
5. Push the branch and tag to remote `git push -u origin hotfix-v0.10.1-weirdbehavior --follow-tags`.
6. Deploy the tag `v0.10.1` to the production environment.

### Issue and Pull Request Labels

The labels are loosely grouped by their purpose, but it's not required that every issue have a label from every group or that an issue can't have more than one label from the same group.

#### Type of Issue and Issue State

| Label name | Description |
| --- | --- |
| `enhancement` | Feature requests. |
| `bug` | Confirmed bugs or reports that are very likely to be bugs. |
| `question` | Questions more than bug reports or feature requests (e.g. how do I do X). |
| `help-wanted` | The Scriba team would appreciate help in resolving these issues. |
| `more-information-needed` | More information needs to be collected about these problems or feature requests (e.g. steps to reproduce). |
| `needs-reproduction` | Likely bugs, but haven't been reliably reproduced. |
| `duplicate` | Issues which are duplicates of other issues, i.e. they have been reported before. |
| `wontfix` | The Scriba team has decided not to fix these issues for now, either because they're working as intended or for some other reason. |
| `invalid` | Issues which aren't valid (e.g. user errors). |

#### Topic Categories

| Label name | Description |
| --- | --- |
| `grammar` | Grammar related issue. |
| `semantics` | Semantics related issue. |
| `plagiarism` | Plagiarism related issue. |
| `academic-style` | Academic style related issue. |
| `citation` | Citation related issue. |
| `lti` | LTI related issue. |

#### Pull Request Labels

| Label name | Description |
| --- | --- |
| `work-in-progress` | Pull requests which are still being worked on, more changes will follow. |
| `needs-review` | Pull requests which need code review, and approval from maintainers. |
| `under-review` | Pull requests being reviewed by maintainers. |
| `requires-changes` | Pull requests which need to be updated based on review comments and then reviewed again. |
| `needs-testing` | Pull requests which need manual testing. |
