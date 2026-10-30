# filesystem-deny-write-system-config

## Pattern

```
Edit(//etc/**)
Edit(//private/etc/**)
Edit(~/.ssh/**)
Edit(~/.gnupg/**)
Edit(~/.aws/credentials)
Edit(~/.aws/config)
Edit(~/.kube/config)
```

Deny rules for the Write, Edit, and NotebookEdit tools. A deny rule wins over every allow rule in every mode, including `bypassPermissions`. On macOS `/etc` is a symlink to `/private/etc`, and Claude Code 2.1.268 or later applies a deny written through the symlink at the real location as well. The second spelling is listed so the rule does not depend on that behavior.

Before October 30, 2026 the only `/etc` and `~/.ssh` write denials in this harness were two advisory files under `~/.claude/rules/` (`deny-etc-writes-broad.md` and `deny-ssh-key-writes.md`), written in the voice of enforced rules but loaded as instructions. Instructions are advisory per AP.1. These three entries are the enforced form, and the advisory files now point here.

The last four entries, added after the second premortem round, cover the other credential stores the rm hook protects, so a `Write` to a credential file has a rule-layer deny behind the hook's `ask`. Reads are not denied by this rule. `Read(~/.ssh/**)` lives in the templates' deny lists for adopters. The Mac reference build leaves SSH config readable for diagnostics, per the advisory file's stated intent. Bash is covered only in part: `echo x > /etc/hosts` is a redirection, which Claude Code checks against Edit rules, while `/usr/bin/sudo tee /etc/hosts` is stopped by `Bash(sudo:*)` only when spelled `sudo`. The OS owner on `/etc` is the backstop for the rest.

## Threat addressed

`foundation/01-threat-model.md` T.2 (prompt injection through agent inputs) and T.6 (credential and secret exposure). A write to `~/.ssh/authorized_keys` is a persistent backdoor. A write to `~/.ssh/config` can redirect connections or disable host-key checking. A write under `/etc` can change PAM, sudoers, hosts, or cron.

## Why deny, not ask

No routine development task writes inside `.ssh` or `/etc`. `/etc/cron.d` was carved out as an allowed exception in the advisory file set. Claude Code has no specificity precedence between allow and deny, deny wins, and a write there needs root in any case, so the exception is retired.

## Test

```
echo '{"tool_name":"Write","tool_input":{"file_path":"/etc/hosts"}}'
echo '{"tool_name":"Edit","tool_input":{"file_path":"/private/etc/hosts"}}'
echo '{"tool_name":"Write","tool_input":{"file_path":"~/.ssh/authorized_keys"}}'
```

Each is expected to be refused by the rule layer before any hook runs. a pipe test cannot exercise the rule layer, so confirm in a live `default`-mode session. `PreToolUse-external-write-gate.py` also asks for the same paths, which its test matrix records, so the deny has a second layer behind it.

## Provenance

October 30, 2026. Foundation: T.2, T.6. Replaces the advisory-only `/etc` and `.ssh` write denials.
