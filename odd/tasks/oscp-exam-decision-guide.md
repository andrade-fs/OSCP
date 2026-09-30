# OSCP Exam Decision Guide

## Objective
Turn the existing OSCP vault into an offline, decision-oriented field guide that helps a candidate move from observed evidence to the next safe, in-scope enumeration or exploitation step during the exam.

## Problem
The repository has strong breadth but several exam-critical links lead to blank notes, offline regeneration/search sources are missing, and installation, verification, and evidence paths disagree. A candidate can find a port or service index but may not reach a usable command sequence, stop condition, or evidence checklist.

## Scope
- Repair the offline-documentation contract before adding new navigation.
- Provide scenario-driven guides for reconnaissance, web, Linux/Windows privilege escalation, AD, credential use, pivoting, and reporting.
- Make key tool and technique notes scannable offline with expected evidence, next actions, and stop conditions.
- Align documented paths and verification behavior with the installer.

## Constraints
- Preserve the repository's Spanish documentation convention.
- Keep every command and technique explicitly marked as exam-scope verified, lab-only, prohibited, or pending current-policy verification.
- Do not state an OffSec policy conclusion without an accessible authoritative source; the official Exam Guide currently returned HTTP 403 during retrieval on 2026-03-13.
- Keep markdown usable from Obsidian and a terminal without generated/runtime dependencies.
- No package installation or tool execution against targets is part of this documentation work.

## Acceptance criteria
- The root entry point links to a scenario index that tells the reader what to do after common observations.
- All high-traffic technique links resolve to non-empty, actionable notes or clearly labelled index stubs.
- The documented offline search/regeneration and reference mirrors are either restored and checked or their promises are removed.
- Installer, verifier, walkthrough, and evidence paths share one documented source of truth.
- Each playbook contains: entry condition, first actions, decision points, evidence to record, and stop/park condition.
- Link and structural checks run successfully or any unavailable check is recorded.

## Delivery strategy
- Incremental, reviewable documentation slices; no commit or publication unless the user explicitly requests it.
- Expected first slice: correctness and broken offline paths before new prose.

## Tasks

- [x] ODG-01 Audit tooling, setup, and OSCP workflow coverage.
  - Evidence: read-only audits on 2026-03-13 found installer/verifier path drift, scope contradictions, missing BloodHound GUI/CE documentation, thin wordlist coverage, and unsafe/deprecated command patterns.
- [x] ODG-02 Assess note usability and decision-path coverage.
  - Evidence: read-only assessment on 2026-03-13 found missing `_sistema/datos/`, missing GTFOBins reference targets, approximately 57 blank technique-index notes, and duplicated/divergent entry points.
- [x] ODG-03 Define the offline guide information architecture and policy labelling model.
  - Route: delegated direct; trigger: architecture spans multiple documentation areas.
  - Evidence: design completed on 2026-03-13. First slice adds a single scenario router, templates, a document-health ledger, and a stdlib link checker while preserving generated-layer files as read-only until source data is recovered.
- [x] ODG-04 Repair documentation-contract failures and add structural validation.
  - Route: delegated direct; trigger: multi-file write.
  - Evidence: router, templates, health ledger, and stdlib first-slice checker created. Parent and independent verification passed: 260 local references, 0 errors, `git diff --check`, AST parse, and byte-level UTF-8/NUL/final-newline checks.
- [ ] ODG-05 Create scenario and critical service/technique decision cards.
  - Route: delegated direct; trigger: multi-file write. Split to protect review focus.
  - [x] ODG-05A AD decision playbooks (credentials, Kerberos, Certipy/ADCS) and their router links.
    - Evidence: four cards and router links created; `ad-slice` validates 481 references with 0 errors. Anchor validation was added after independent review found fragments unchecked; correction independently passed.
  - [ ] ODG-05B Service, web, pivoting, and Linux/Windows privilege-escalation decision cards. Split to keep reviewable slices.
    - [ ] ODG-05B1 Web and core service decision cards.
      - [x] ODG-05B1a HTTP, SMB, and LDAP decision cards.
        - Evidence: three cards added; `core-services-a` validates 642 references with 0 errors. Independent review caught an unsupported sqlmap prohibition claim; it was corrected and independently approved.
      - [x] ODG-05B1b NFS, MSSQL, and WinRM decision cards.
        - Evidence: three cards added; `core-services-b` validates 829 references with 0 errors and independent verification approved the slice.
    - [ ] ODG-05B2 Linux/Windows privilege escalation, pivoting, and transfer decision cards. Split to keep reviewable slices.
      - [x] ODG-05B2a Windows low-privilege decision card.
        - Evidence: manual triage card added and independently verified; `windows-privesc` validates 909 references with 0 errors.
        - Route a low-privilege shell through manual triage before/alongside winPEAS, including Winlogon/AutoLogon registry checks, services, scheduled tasks, token privileges, writable paths, saved credentials, and a stop/park rule.
      - [ ] ODG-05B2b Linux privilege-escalation decision card.
      - [ ] ODG-05B2c Pivoting and transfer decision cards.
  - Check: each card has entry condition, ordered next actions, evidence, stop condition, and links.
- [ ] ODG-06 Perform a read-only navigation and offline-readiness verification.
  - Route: delegated verification; trigger: verification command/readback.
  - Check: links, paths, markdown structure, and documented commands are internally consistent.

## Current verification evidence
- Repository cloned at `/private/tmp/OSCP` on branch `docs/oscp-exam-decision-guide`.
- The generated untracked `.codegraph/` directory created by delegated exploration was removed before source changes were evaluated.
- Engram mirror saved and read back as observation `6678` under `odd/oscp-exam-decision-guide/tasks`.

## Next step
Create the focused AD decision-playbook slice, then validate its navigation and exam-scope labels independently.
