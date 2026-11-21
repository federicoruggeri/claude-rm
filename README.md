# claude-rm

`claude-rm` deletes selected Claude Code sessions from the local machine.
A session is one saved conversation, which `claude --resume` lists.
The script lists every session in [fzf](https://github.com/junegunn/fzf), an interactive fuzzy finder for the terminal.
It then removes the sessions you pick.
Claude Code itself offers `claude purge`, which deletes data for a whole project rather than for single sessions.

## Requirements

The script needs Python 3.8 or later and `fzf` on `PATH`.
It uses only the Python standard library.

## Installation

Clone the repository and link the script into a directory on `PATH`.

```sh
git clone https://github.com/federicoruggeri/claude-rm.git
ln -s "$PWD/claude-rm/claude-rm.py" ~/.local/bin/claude-rm
```

## Usage

```sh
claude-rm           # list sessions from every project, newest first
claude-rm PATTERN   # open the picker with PATTERN as the initial query
```

Each row shows the last modification time, the project directory, and a title.
The title is the name set with `/rename` or `claude --name`.
Without such a name, the row shows the title Claude Code generates for the session.
When neither exists, the row shows the first prompt of the session.
The preview pane shows the first eight prompts of the highlighted session.

Press Tab to select several sessions and Enter to delete them.
The script lists the selection and asks for confirmation before deleting anything.
Any answer other than `y` cancels the deletion.
The picker then reopens with an updated list, and Esc closes it.

## What gets deleted

Claude Code stores each session as `~/.claude/projects/<project>/<session-id>.jsonl`.
For each selected session, the script removes three items:

1. the transcript file `<session-id>.jsonl`;
2. the directory `~/.claude/projects/<project>/<session-id>/`, which holds subagent transcripts;
3. the directory `~/.claude/file-history/<session-id>/`, which holds file edit history.

Deletion is permanent and cannot be undone.

## Limitations

Do not delete the session that is currently running, because Claude Code recreates its transcript on the next write.
The script reads the transcript format of Claude Code 2.1.330, which may change in later releases.
