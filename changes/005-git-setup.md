# 005 — Git Repository, Black, and Git-Flow

Installed black inside WSL Ubuntu using pip3 so that Python code formatting is available as a command-line tool.
Added a Git-Flow section to the project CLAUDE.md covering branch structure, naming conventions, commit message rules, and hard rules that Claude must follow on every git operation.
Initialised a local git repository in the pet-store-api project directory inside WSL.
Wrote a pre-commit hook at .git/hooks/pre-commit that finds all staged Python files, runs black to reformat them in place, and re-stages the results before the commit proceeds.
Made the pre-commit hook executable so git can run it automatically on every commit.
Set the initial branch name to main to align with Git-Flow conventions.
Staged all project files and created the first commit with the message GENESIS.
Created the develop branch from main as the ongoing integration branch per Git-Flow.
