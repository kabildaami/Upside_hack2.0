# EduNova — Private Journal Workspace UI

A focused, viewport-sized journal interface for senior students. It uses **existing** encrypted journal CRUD and **existing** OpenRouter streaming endpoints. This is a **frontend-only** patch — no database migration, backend/router overwrite, or credential changes.

## Install

**Prerequisite:** the earlier `EduNova_Private_Journal_Live_AI_Companion_Patch.zip` has already been installed, including SQL migration 16 and a working Fernet key. The installer will stop without changing files if the integration is missing.

Extract this ZIP so that `EduNova_Journal_Workspace_UI` is inside `C:\Users\Adam\Desktop\upside_hack`, then run:

```powershell
cd C:\Users\Adam\Desktop\upside_hack
python .\EduNova_Journal_Workspace_UI\tools\install.py .
cd frontend
npm run build
npm run dev
```

Hard-refresh Chrome after the frontend restarts. If installed from another directory, replace the patch path with its actual location.

## What changes

- **Left entry rail:** recent encrypted entries, New reflection, choose past entry. Only this list scrolls when long.
- **Right active workspace:** `Read entry` / `Write` and `Reflect with AI` tabs, no nested long dashboard page.
- **Write:** full-height distraction-free editor, Save button pinned at bottom; after saving, its newly created entry is selected.
- **Reflect:** selected entry context above a streamed AI chat, input and explicit external-AI consent pinned to bottom. Chat history remains scoped to the selected entry.
- **Safety:** separate Support dialog keeps trusted contacts and the existing `request-human-help` endpoint. Recording a help request **does not send an alert**; warning text remains explicit.
- **Privacy:** loading the journal does not call OpenRouter; the student must tick consent to send their entry and conversation. Encrypted storage, backend ownership checks, and original Fernet key are unchanged.
- **Compatibility:** installer only replaces the diary JSX branch in `SeniorAgentStudio.tsx`; does not alter junior/teacher layouts, senior tools/sidebar, login, admissions, or any API.

## Local acceptance checks

1. Log in as Mehdi, open **Tools → Private journal**; verify header + entries + editor fit on screen.
2. Save a new entry and confirm that it is selected in the left list.
3. Switch to **Reflect with AI**. Without the consent checkbox, Send should be disabled.
4. Opt in, send a message, check streamed response and per-entry conversation history. Switch between entries; histories must remain separate.
5. Delete a test entry and confirm it no longer appears; its linked AI turns are deleted through DB cascade.
6. Test **Support**. Its recorded help requests do not actually notify contacts.

Note: genuine narrow-screen accessibility may require internal scrolling for long content or safety forms. The top-level page is never intentionally made taller by this component.

## Validation

Run `npm run build` in your project. Browser rendering and live API integration must be checked locally. The installer backs up overwritten files as `.before_diary_workspace.bak`, once per file.
