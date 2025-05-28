# User-Specific Development Preferences

## CRITICAL REMINDERS
- **WSL/Windows Hybrid**: Development in WSL, app runs in Windows 11, Docker in WSL2 mode
- **Skill Level**: User is a novice developer - provide clear, step-by-step guidance

## USER PREFERENCES

### Development Approach
- **ONE STEP AT A TIME**: Never provide multiple steps - wait for confirmation between each

### Learning Style
- User learns best with single instructions tested before proceeding
- Explain WHY something works, not just HOW
- Use analogies connecting new concepts to familiar ones
- Clarify the purpose of each file and component

### Before Writing Code
- **PREVIEW DEVLOG**: Check Devlog.md for past issues and resolutions
- **REVIEW SCOPE**: Understand project scope and implementation from attached files
- **UNDERSTAND DEPRECATIONS**: Note deprecated commands and fixed issues from Devlog

### After Major Work
- Write a Devlog.md update for user to append
- Recommend updates to Scope.md, implementation.md, README.md when needed
- keep updating file and folder architecture if new files are added, including their detailed purpose
- Keep track of architectural changes

### Debug Approach
- Provide isolated, single changes only
- Test each change before suggesting the next
- creating test files that the user needs to execute manually is ok, provided they are deleted after problem is fixed
- Track these test files so they can be continually purge if we forget to delete them

### File Preferences
- NO unnecessary file creation, if the architecure lends itself for a new file due to efficiency or adhering to modal methodology, then it is ok to create a file.  However, the behaviour should be controlled.
- ALWAYS prefer editing existing files
- NEVER proactively create documentation unless requested, instead fit updates into existing project documents
- Delete temporary files after use

## TECHNICAL REMINDERS

### About the Developer
- Hobbyist/novice programmer eager to learn
- Good Windows command line familiarity
- Strong hardware and Windows OS knowledge
- Minimal Linux experience
- Very novice with Python
- Basic database understanding (theoretical)
- Needs help with embeddings, vector search, LLMs

### Key Project Details
- Virtual environment: `venv_nemo` (NOT `venv`)
- Self-aware mode password: "dev-mode-2024"
- NIM embeddings required (no fallback)
- Application tested on Windows despite WSL development

## WORKFLOW REQUIREMENTS

### Step-by-Step Process
1. Understand the request fully
2. Review relevant project files
3. Ask clarifying questions if needed
4. Provide ONE action to take
5. Wait for user confirmation
6. Proceed to next step only after verification

### Documentation Updates
- Track major changes for Devlog.md and Todo files.
- Note when Scope.md or implementation.md need updates
- Keep README.md current with setup changes