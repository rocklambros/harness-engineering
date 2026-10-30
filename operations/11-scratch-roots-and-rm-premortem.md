# Post-Mac 11: Adversarial premortem of the scratch-root and rm protected-paths change

Artifact under review: branch `feature/external-write-gate-private-root` of `rocklambros/harness-engineering`, the working tree as of October 30, 2026, before any commit. Claude Code 2.1.314 installed. Method: the adversarial-premortem skill, six perspectives per round run as independent subagents with clean context, cross-attacked and calibrated by the orchestrator. Data Scientist was skipped in every round: the artifact has no data, labels, or statistics. Security Architect was spawned in Round 1 and skipped in Round 2, where its Round 1 findings all mapped onto code the Red Teamer re-attacked.

The first landing of the change (the state Round 1 attacked) widened the external-write gate's scratch exemption to the whole of `/private`, added a first-draft `PreToolUse-bash-deny-rm-protected-paths.py`, and removed five dead `Write(path)` rules. Round 1 produced the remediation recorded below. Round 2 attacked the remediated tree.

## Round 1. Problem framing and premises.

Perspectives spawned: Red Teamer, Engineer, Security Architect, MLOps/SRE, Governance/Risk. Skipped: Data Scientist (nothing anchored).

Premortem narrative. Six months out, an unattended bypass-mode session launched from the Desktop app has no `python3` on its PATH. Every deny the harness documents is a non-blocking hook error the runtime walks past. An injected instruction in a README under `/tmp` writes a `CLAUDE.md` into the clone with no prompt, because the whole of `/private` was exempt, and a later session loads it. The operator, told the harness fails closed, never looked.

Findings surviving at Plausible or above, merged across perspectives.

1. Every hook registration is fail-open. Impact: High. Confidence: Likely (prior Very likely for the mechanism from all five perspectives, moved down one band because the trigger, a hook that cannot start, needs an environment event. The SRE and Security Architect brought independent evidence, a bare-PATH launch and `disableAllHooks` in a project settings file). Evidence anchor: Claude Code hooks reference, "Non-blocking error ... The action goes ahead, except for hooks whose failure blocks the action, for example a hook with `onFailure` set to `"block"`. Requires Claude Code v2.1.295 or later." `grep onFailure` over every settings file returned nothing. `mac/harness/hooks/README.md` line 5 asserted "All hooks fail closed per AP.8." Failure mode: a missing interpreter or a renamed script turns every deny into a silent allow. Blind spot: AP.8 was written as a property of the scripts, not of the registration, and the runtime's semantics changed under the pin. Opportunity cost of leaving it: the whole deterministic layer is conditional on process health.

2. The `/private` root is wider than the motivating gap. Impact: Medium (High under bypass). Confidence: Likely (measured on the machine: `/var/folders/.../0`, `C`, `X` hold persistent application state, `find /private/var -maxdepth 2 -perm -o+w` lists `/var/db/mds`, `/var/db/DiagnosticsReporter`, `/var/OOPJit`). The Security Architect found that `getconf DARWIN_USER_TEMP_DIR` returns the per-user temp directory with no environment dependency, which is the narrow fix. Blind spot: the exemption was reasoned from directory names, not from an inventory of what is writable under them.

3. The `/etc` carve-out cites a deny rule that does not exist. Impact: Medium. Confidence: Very likely (grep over every settings file. The cited `~/.claude/rules/deny-etc-writes-broad.md` is advisory prose with a precedence model Claude Code does not have). The new `Edit(//private/**)` allow rule pre-approved `/private/etc` at the rule layer while the hook header claimed the rule layer denied it.

4. The first-draft rm hook had reproducible bypasses. Impact: High. Confidence: Very likely (each one pipe-tested). Bare `/System/Volumes/Data` and `/Volumes/<drive>`. Case-folded `/users/<name>` on APFS. Wrappers outside a fixed allowlist (`timeout 10`, `nice -n 5`, `caffeinate`, `setsid`, `ionice -c 3`, `doas`). `cd ~ && rm -rf *` and `cd .. && rm -rf *` (the hook resolved relative targets against the session cwd, not the directory the command changed into). Dot-globs `~/.*`, `~/{*,.*}`, `~/?*`. Named children of home that hold credentials (`~/.ssh`, `~/.gnupg`, `~/.aws`) and the config root itself (`~/.claude`, `~/.claude/hooks`), whose deletion disables the controls. A `~user/child` false positive. The protected set was derived from the May rule patterns rather than from the reversibility test.

5. The scratch exemption short-circuited the pre-trust carve-out. Impact: High under bypass, Medium otherwise. Confidence: Likely (pipe-tested: `/tmp/clone/.claude/settings.json`, `/tmp/clone/.mcp.json`, `/tmp/clone/.git/hooks/pre-commit` all allowed while the same paths under any other repo asked). The Class 4 carve-out existed for exactly these names and was never consulted on the scratch path.

6. "CRUD never prompts" overstated what was delivered. Impact: Medium. Confidence: Likely. Deletes go through Bash and follow the permission mode. Claude Code's critical-path check prompts on `rm -rf "$TMPDIR"/*` and on `rm -rf .` from a scratch cwd in every mode. The first-draft hook denied `rm -rf /tmp/*`. `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS` is documented to have no effect while any deny or ask rule targets Bash, Edit, or Read, which the harness ships.

7. The binding documents did not carry the decision. Impact: Medium. Confidence: Very likely. `foundation/01-threat-model.md` and both CLAUDE.md files listed four destructive hooks while the settings comments listed five, the T.2 residual for the widening appeared nowhere, and JOURNEY.md had no entry.

8. The deploy tool selected a stale template and would instruct the operator to remove every Python hook. Impact: High. Confidence: Very likely (dry run reproduced: candidate order listed the template first against the script's own comment, and `mac/harness/settings.json.template` registered only the four shell hooks).

9. Cross-platform parity was broken at the rule layer. Impact: Medium. Confidence: Very likely. Jetson received the hook but not the allow rules, kept the dead `Write(./**)`, and carried `Read(/etc/shadow)` with a single slash, which anchors at the settings source rather than the filesystem root.

10. The live `~/.claude/settings.json` was changed without re-attestation in `audited-hashes.json`. Impact: Medium. Confidence: Very likely. The SessionStart audit checks `<cwd>/.claude/settings.json`, so a session started from `$HOME` would block.

11. The verification matrix lived in a scratchpad. Impact: Medium. Confidence: Likely. The 80-case run was durable only in a session transcript, and one live probe misdiagnosed a correct allow as a reload failure.

12. The principle every gate cites did not exist. Impact: Medium. Confidence: Very likely. Fifteen citations of "foundation/02 Principle 3 (reversibility-weighted risk)" pointed at a file whose sections are AP.1 through AP.10.

13. The allow rules missed the `$TMPDIR` spelling. Impact: Medium. Confidence: Likely. `$TMPDIR` is `/var/folders/...`, which neither `//tmp/**` nor `//private/**` matches as written.

14. A version floor was attributed to the wrong behavior, dates mixed ISO and Month Day, Year, and the tree bundled several decisions. Impact: Low. Confidence: Very likely.

15. A hook's `ask` prompting under `bypassPermissions` is observed, not documented. Impact: Medium (bypass sessions only). Confidence: Plausible. The only textual support is one troubleshooting bullet. A minor bump that aligns the behavior with the mode's definition would remove the write gate's last prompt silently.

Cross-attack log.

The SRE rated finding 1 Critical. The Red Teamer and Security Architect each raised the native critical-path check as the backstop that still prompts in a terminal and denies in the Desktop app. Adjudicated to High: the backstop does not cover `/usr`, `/private/<name>`, credential stores, or the config root, which is most of the hook's protected set, and a prompt is not a deny. The Engineer's counterargument that `onFailure: "block"` turns any crash into a wedge of every tool call was accepted as the cost and resolved by AP.8's own text ("a false positive costs a re-run"): the flag goes on the four destructive-class hooks only.

Governance and the Red Teamer disagreed on `rm -rf /tmp/*`: Governance read the hook's deny as a correct top-level-directory rule, the Red Teamer read it as a contradiction of the operator's scratch intent. Resolved in favor of the operator: the glob form of a scratch root passes, the root itself denies, and the write gate and rm hook now share one scratch-root definition.

The Security Architect's working-directory finding depended on `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS` disabling the native check. Governance showed the variable is inert while the harness's deny rules exist. Confidence moved from Plausible to Unlikely for the stated trigger, but the fix (protect cwd and its ancestors) was kept because it costs nothing and the Desktop app path denies natively anyway.

Four perspectives reported the `/etc` finding from the same grep. Treated as one finding with one evidence base, not four.

## Remediation that landed before Round 2

Finding 1: `"onFailure": "block"` and the `python3 -I <path>` form on the four destructive-class hooks in all four settings files. Both new hooks exit 2 on a non-JSON payload and on any exception. The rm hook denies through exit 2 and stderr, the documented form an allow rule cannot override. `_claude_code_hook_onfailure_floor` recorded. README and T.7 rewritten to say which hooks fail closed and why the others do not.

Findings 2, 5, 13: scratch roots are `/tmp`, `$TMPDIR`, and `getconf DARWIN_USER_TEMP_DIR`. `/var/tmp` gated again. `.git`, the pre-trust names, and the config root never exempt. Allow rules narrowed to `//tmp/**`, `//private/tmp/**`, and `//var/folders/*/*/T/**` in both spellings.

Finding 3: carve-out removed (no longer reachable). `Edit(//etc/**)`, `Edit(//private/etc/**)`, `Edit(~/.ssh/**)` added as enforced denies with `filesystem-deny-write-system-config.md`. The advisory files point at the enforced rule.

Finding 4: rm hook rewritten. Every token position is inspected, `cd` and `pushd` are tracked across segments with an unresolvable `cd` making later `.`, `..`, and glob targets deny, any glob character in the last component is the glob form of its directory, mounted-volume shapes and the bare Data volume are protected, case folds on macOS and Windows, `~user` expands, cwd and its ancestors are protected (the glob of cwd passes), credential stores and the config files deny on any rm. 143-case matrix committed under `mac/harness/hooks/tests/`, mirrored to Jetson and Windows.

Finding 6: the decision is restated everywhere as "create, read, and update through the file tools never prompt. Deletes follow the permission mode" with the native-check shapes listed.

Finding 7: five-hook lists in `foundation/01`, both CLAUDE.md files, and the live `~/.claude/CLAUDE.md`. T.2 residual paragraph. JOURNEY entry.

Finding 8: `scripts/deploy-harness.sh` prefers `settings.json`. The Mac template registers the same hooks as the reference build. README registration sentence corrected. HARNESS_GUIDE hook coverage rewritten.

Finding 9: Jetson template carries the allow rules, loses `Write(./**)`, anchors the `/etc` reads at `//etc/`. Rule documents and tests mirrored. Jetson CLAUDE.md gains the autonomous-flag paragraph. A deployment runbook written on the managed-store precedent. Windows AP.3 exception recorded.

Finding 11: both matrices committed and referenced from the hook headers, READMEs, and USER_GUIDE.

Finding 12: AP.11 added to `foundation/02` with the two-question test. New and touched citations point at it.

Finding 14: the 2.1.228 sentence corrected. New prose uses Month Day, Year. Hook `Owner:` lines keep the ISO convention of their siblings.

Finding 15: recorded in `bash-deny-rm-rf-root.md` and `filesystem-allow-scratch-roots.md` as the dependency it is. The session-start probe is a tracked follow-up.

Finding 10 (hash registry) is applied after Round 2, once the live settings file is final.

## Round 2. Methodology and code correctness, attacking the remediated tree.

Perspectives spawned: Red Teamer, Engineer, MLOps/SRE, Governance/Risk. Skipped: Data Scientist (nothing anchored), Security Architect (its Round 1 findings all mapped onto code the Red Teamer re-attacked).

Premortem narrative. Six months out, the matrices are green and the headers say "a deny that holds in every mode". An injected cleanup step is spelled `bash <<< 'rm -rf ~'`, or `eval "rm -rf $HOME"`, or `rm -rf ~/**/*`, or `mv ~/.ssh /tmp/x`. The hook, which enumerated program names and one glob shape, says nothing. The deploy script, which now reads the Mac `settings.json`, prints a hooks block whose paths exist only inside the harness checkout, and the operator who pastes it locks every tool call on the first session in any other project.

Findings surviving at Plausible or above, merged across perspectives.

1. The hook enumerated syntactic containers and program names, so a one-token rewrite defeated it. Impact: Critical. Confidence: Very likely (each form reproduced by two perspectives independently). `r''m -rf ~` and `"r"m -rf ~` passed a raw-text pre-filter that ran before tokenization. `eval 'rm -rf ~'`, `bash <<< 'rm -rf ~'`, `echo 'rm -rf ~' | bash`, `for d in ~; do rm -rf $d; done`, and `alias z='rm -rf ~'; z` were not in the container set. `RM -rf ~` and `/bin/RM -rf ~` resolved on the case-insensitive filesystem while the program name was compared case-sensitively. `{rm,-rf,~}` was one token. `cat <(rm -rf ~)` and `echo "$( (rm -rf ~) )"` fell outside a regex that could not span a nested parenthesis. A fourth level of `sh -c` nesting returned None instead of a deny. Blind spot: the matrix tested the wrappers its authors thought of, so 143/143 measured the allowlist, not the boundary.

2. The heredoc stripper ran on raw text with no quote awareness, so `echo "<<EOF"` followed by a newline blinded the scanner for the rest of the command, and `$((1<<3))` did the same. Impact: High. Confidence: Very likely (reproduced).

3. Only the last path component was tested for glob characters, so `rm -rf ~/**/*`, `~/*/*`, `~/Library/*`, and `~/.config/*` resolved to unprotected directories, and the glob of a cwd ancestor (`rm -rf ../.*` from a subdirectory, which reaches `../.git`) passed because the ancestor walk was guarded by the cwd-glob exemption. Impact: High. Confidence: Very likely.

4. `"${HOME%/}"`, `"$(echo ~)"`, and `$DIR/*` were joined to cwd as literal text rather than refused as unknowable. Impact: Medium (the native check flags the glob-under-variable shape). Confidence: Very likely.

5. Deletion by `mv`, `unlink`, `shred`, `find -delete`, and `xargs rm` was out of scope while the native check also covers only `rm` and `rmdir`, so the credential stores, the highest-value protected class, had the weakest coverage. `mv ~/.ssh /tmp/x` additionally lands private keys in the scratch root the same change made prompt-free. Impact: High. Confidence: Very likely.

6. The write gate's inside-cwd test used `abspath`, not `realpath`, so a symlink tracked in a cloned repository (`vendor/sdk -> ~/.claude/hooks`) carried the inside-cwd exemption to the live hooks directory. Its managed-store exemption had the same gap, and its memory exemption accepted any project's memory directory, which is read into that project's next session. Impact: High under bypass. Confidence: Very likely.

7. The write gate's any-repo class exempted the harness's own hook sources, rule documents, deploy script, and workflow definitions, which the deploy script copies into the config root the gate protects. Impact: High. Confidence: Very likely.

8. The rm hook's config-root protection listed the files the harness authors and missed `skills/`, `agents/`, `mcp.json`, `.credentials.json`, `plugins/`, and `~/.claude.json`, which change what loads at session start. Impact: Medium. Confidence: Very likely.

9. Four daily workflows were denied: `git rm -r --cached .`, `docker exec web rm -rf /data` and `ssh host rm -rf /srv` (another filesystem), and `rm -rf ~/.kube/cache` and `~/.aws/sso/cache` (routine resets inside a credential store). Impact: Medium. Confidence: Very likely.

10. `scripts/deploy-harness.sh`, after the Round 1 reorder, read the Mac `settings.json` whose hook paths are `${CLAUDE_PROJECT_DIR}/mac/harness/hooks/...`, substituted only `{{REPO_ROOT}}`, and would install a hooks block that cannot start outside the harness checkout, which the new fail-closed registrations turn into a block of every Bash, Write, and Edit call. The Jetson runbook rendered the template with a plain `sed` to the wrong directory and probed with `rm -rf ~`, which the rule layer already answers. Impact: Critical on a fresh install. Confidence: Very likely (dry run reproduced).

11. The fail-closed registrations carried no `timeout`, so a hung mount could hold one tool call for the 600 second default before blocking. The shell-form `python3 -I <path>` with an unquoted placeholder would fail on a checkout path containing a space. The matrix failed four cases on Linux because structural names were folded only on Darwin. Impact: Medium. Confidence: Very likely.

12. The record still asserted blanket fail-closed in AP.8, both platform CLAUDE.md files, the T.4 mitigation, and the hooks README dependency section, and added a false claim that the SessionStart audit registers `onFailure: block` when a SessionStart hook cannot block at all. The user-level CLAUDE.md said force push is denied at the rule layer when it is an ask. The version pin admitted every 2.1.x release below the floors the change depends on. Three documents said the native critical-path check does not cover `/usr` when it covers every top-level directory. 2.1.295 was described as a change in failure semantics when it added the opt-in flag. The README said the reference file and the template carry the same registrations when they differ by six hooks and the live file by six more. The new hook cited "Threat actors #1", a vocabulary with no section in the threat model. The advisory rule files under `~/.claude/rules/` contradicted themselves after annotation. Impact: Medium (High for the fail-closed sentences in the files adopters copy). Confidence: Very likely (every item a direct text comparison).

13. `--bare` is documented to become the default for `-p` runs and skips hook discovery, which would remove every gate from exactly the unattended runs the harness designs for. Nothing at session start proves the four gates can start or reads the version floor. No rollback procedure was written. Impact: High when the flip lands. Confidence: Likely (vendor statement, date unknown).

14. A cloned repository that ships `disableAllHooks: true` in `.claude/settings.json` turns every hook off for that session, and the SessionStart audit that would notice can only flag. Impact: Critical if it fires. Confidence: Plausible (needs the operator to open a hostile repository, which is the T.3 scenario the audit exists for). Claude Code's `ConfigChange` event can block and is the right home for the hash check.

Cross-attack log.

The Red Teamer rated the container-enumeration finding Critical. The Engineer had found the same forms at High with the counterargument that Claude Code's own parser reads `sh -c` and substitutions. Adjudicated Critical: the vendor's documented nested-form list omits `eval`, here-strings, and pipes into a shell, so the forms evade both layers.

The Engineer's deploy-script finding and the SRE's were the same finding from a dry run. The SRE added the Jetson runbook's rendering path and probe, which the Engineer had not run. Adjudicated Critical on the fresh-install path, Medium for the daily dry run.

Governance's finding that SessionStart cannot block was corroborated by the Red Teamer from the hooks reference table and by the hook's own docstring. The Red Teamer's `disableAllHooks` scenario is the exploit. Governance's is the documentation. Adjudicated as two findings: the documentation is fixed in this change, the `ConfigChange` gate is the tracked follow-up with a tail-risk note.

The Red Teamer argued the `:*` rules might be inert because the colon form is also the parameter-matching syntax. The permissions reference states in one sentence that `Bash(ls:*)` matches the same commands as `Bash(ls *)`, which three perspectives quoted in Round 1. Dropped to Unlikely and recorded in the ledger. The rule documents' bare `echo` test lines were rewritten to say that the rule layer needs a live default-mode read-back.

## Remediation that landed after Round 2

Findings 1 through 5: the rm hook was rewritten a third time. The raw-text pre-filter is gone and the program name is folded on case-insensitive filesystems. Brace lists expand. `eval`, `alias` values, here-strings, and pipes into a shell are scanned, the previous segment's tokens serving as the script for a pipe sink. `for X in <literals>` binds the variable for the rest of the line. Substitutions are found by a balanced-parenthesis scanner that also reads `<(...)` and `>(...)`. Nesting beyond three levels denies. The heredoc operator is recognized only outside quotes and not after a digit or identifier, and a body with no terminator is scanned rather than stripped. A glob at any depth is the glob form of its deepest literal ancestor. The glob of an ancestor of cwd denies. Only the glob of cwd itself passes. `$HOME`, `$TMPDIR`, `$PWD`, and for-bound variables resolve, a `${NAME%...}` modifier is read as `$NAME`, and any other variable or substitution as a recursive target denies. `mv` is judged on its sources, `find` with `-delete` or `-exec rm` on its start paths as globs, `unlink`, `shred`, and `srm` as removers, and `xargs` with a remover on the previous segment's tokens as globs. A directory that contains a credential file (`~/.aws`, `~/Library`) is protected on recursive or glob removal. The config root is protected in full except an explicit cleanup allowlist, and `~/.claude.json` and the hook's own directory are protected. `git rm` passes, and an rm after a remote or container program passes. Credential-store `cache` and `logs` directories pass. Structural names fold on every platform. The matrix grew to 221 cases plus a known-gap list that reports, rather than passes, the forms the hook does not judge.

Findings 6 and 7: the write gate resolves both the target and cwd before the inside-cwd test, resolves managed-store paths, limits the memory exemption to the current session's project, and refuses the exemptions for any `hooks/`, `rules/`, `agents/`, `skills/`, `scripts/`, or `.github/workflows/` component in both the scratch and the any-repo classes. The matrix grew to 42 cases including an in-cwd symlink and the harness repository's own paths.

Finding 8: the config root is protected by exclusion rather than by list.

Finding 9: `git rm`, remote programs, and credential cache directories pass, each as a matrix row.

Finding 10: the deploy script substitutes both placeholder families, fails with exit 2 if a placeholder survives in a hook path, and ignores prose keys when diffing the hooks block. The Jetson runbook renders through the deploy script, prints every registered path with an existence check, registers at user level, probes with `rm -rf /usr`, and refuses to record the port as deployed below the version floor.

Finding 11: the four registrations use the exec form (`"command": "python3", "args": ["-I", "<path>"]`) with `"timeout": 10` in all four settings files.

Finding 12: AP.8 scoped to the destructive class. Both platform CLAUDE.md files, the hooks README, and T.4 say which hooks fail closed. The SessionStart audit is described as a flag everywhere. The user-level CLAUDE.md says force push asks. The version pin is `>=2.1.295,<2.2` with the floors listed in the settings comments and both CLAUDE.md status sections. The native check is described from the published list. 2.1.295 is described as the first way to fail closed. The README states what each settings file carries. The new hook and the touched rule document cite T.2 and T.6. The three advisory files are rewritten in the present tense with a history paragraph, and the force-push file names the ask as the control. A T.4 residual paragraph records the rm hook's scope and relaxers. `Edit` denies for `~/.gnupg`, `~/.aws/credentials`, `~/.aws/config`, and `~/.kube/config` give the credential stores a rule-layer floor. `Bash(Git:*)` is respelled `Bash(git:*)`.

Finding 13: a "Rolling back a gate" section in HARNESS_GUIDE. `--bare` recorded in T.7 and in the rm hook header as a relaxer. The unattended launcher, the session-start probe, and the registration drift check are tracked follow-ups in JOURNEY.

Finding 14: recorded in T.4 as an accepted residual with the `ConfigChange` gate as the follow-up.

## Dropped ledger

The `:*` rules are inert parameter-matching syntax (Red Teamer, Round 2): posterior Unlikely, because the permissions reference states that `Bash(ls:*)` matches the same commands as `Bash(ls *)`. Trigger that would raise it: a `/permissions` read-back in a default-mode session that lists the rules under a parameter heading or a startup warning naming them.

Root-launched sessions write to root-owned trees under `/private` with no prompt (SRE, Round 1): posterior Unlikely, and moot once the scratch roots were narrowed.

The working-directory removal depended on `CLAUDE_CODE_EVEN_MORE_DANGEROUSLY_SKIP_PERMISSIONS` disabling the native check (Security Architect, Round 1): posterior Unlikely, because the variable is documented to have no effect while any Bash, Edit, or Read deny or ask rule exists. The cwd protection was kept because it costs nothing.

The x86_64 Linux branch of the drift check maps to a `linux/harness/hooks` directory that does not exist (SRE, Round 1): Low impact, pre-existing, out of scope.

The deploy script's orphan check flags `PostToolUse-semgrep.sh` as an orphan while it is the deployed rename of `post-tool-use-semgrep.sh` (Engineer, Round 2): Low, pre-existing, out of scope.

Tail risks (Critical, irreversible, below Plausible): none. The `disableAllHooks` scenario sits at Plausible and is in the body.

## Convergence statement

Two rounds completed. Round 2 against the remediated tree still produced Critical and High findings, all of which were closed before the commit and added to the matrices. A third round was not run: the remaining open items are tracked follow-ups with owners rather than unexamined surface (the `ConfigChange` gate, the registration drift check, the unattended launcher, the session-start probe, the live default-mode rule-layer read-back, and the five older hooks' threat citations), and the user asked for the change to land. The stop signal is partial, and this record says so.

## Prioritized remediation plan (all items below landed in this change unless marked follow-up)

1. Fail-closed registrations with exec form and a 10 second timeout on the four destructive-class hooks. Owner: harness engineer. Verified by reading `onFailure`, `args`, and `timeout` back from all four settings files.
2. Rm hook third revision against every reproduced bypass. Owner: harness engineer. Verified by the 221-case matrix on the live copy.
3. Deploy script placeholder handling and Jetson runbook rendering. Owner: harness engineer. Verified by the Mac dry run reading `settings.json` with no placeholder error.
4. Write gate realpath containment, scoped managed stores, executable-tree carve-outs, scratch roots from `getconf`. Owner: harness engineer. Verified by the 42-case matrix.
5. Enforced `Edit` denies for `/etc` and the credential stores. Owner: harness engineer. Verified by reading the deny lists back.
6. Documents of record aligned (AP.8, AP.11, T.2, T.4, T.7, three CLAUDE.md files, guides, READMEs, rule docs, advisory files). Owner: harness engineer. Verified by the prose scan and the drift check.
7. Follow-up: a `ConfigChange` hook that blocks on an unaudited settings hash. Owner: harness engineer. Verified when a cloned repository with an unaudited `.claude/settings.json` cannot change the session's configuration.
8. Follow-up: a drift check that diffs hook registrations across the reference file, the template, and the live settings. Owner: harness engineer. Verified when the check reports the documented live-only extras and nothing else.
9. Follow-up: an unattended launcher that passes `--settings` explicitly and probes the four gates and the version floor at start. Owner: harness engineer. Verified when a `--bare -p` run still denies `rm -rf ~`.
10. Follow-up: the live default-mode read-back of the rule layer and the `Bash(git:*)` respelling. Owner: operator. Verified by a `/permissions` listing and one refused `rm -rf /`.

## Residual risk

Deletion by a program the rm hook does not know (`python`, `rsync --delete`, `git clean`) is unjudged and listed as a known gap in the matrix. An unquoted `echo rm -rf ~` denies as a false positive. A cloned repository that disables hooks through its own settings file is noticed but not blocked until the `ConfigChange` gate lands. Unattended `-p` runs lose every gate when `--bare` becomes the default unless the launcher passes `--settings`. The rule layer's behavior in default mode is documented from the reference and not yet observed in a session on this machine. Each is accepted because the hook, the native critical-path check, the OS, and the operator's review of the diff stand behind it, and each has a tracked owner.
