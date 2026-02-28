# CLAUDE.md

This file provides guidance for AI assistants (Claude and others) working in this repository.

## Repository Status

This is a freshly initialized, empty Git repository. No source code, dependencies, tests, or build configuration have been added yet.

## Git Configuration

- **Remote**: `http://local_proxy@127.0.0.1:26582/git/ichi1251/ichikawa`
- **Commit signing**: Enabled (SSH-based GPG signing via `/tmp/code-sign`)
- **Default identity**: `Claude <noreply@anthropic.com>`

All commits are automatically signed. Do not use `--no-verify` or bypass signing unless explicitly instructed.

## Branch Conventions

- Feature branches should be descriptive and prefixed appropriately (e.g., `feature/`, `fix/`, `claude/`)
- Never push directly to `main` without review
- Always push with `-u origin <branch-name>` to set tracking

## Development Workflow

Since the project has not been initialized yet:

1. Determine the project type and stack before creating any files
2. Create a minimal project scaffold (only what is needed)
3. Add a `.gitignore` appropriate for the chosen stack
4. Add a `README.md` describing the project purpose
5. Commit with a clear message and push to the working branch

## General AI Assistant Guidelines

- Read existing files before modifying them
- Prefer editing existing files over creating new ones
- Keep changes minimal and focused on the stated task
- Do not add unnecessary comments, docstrings, or boilerplate
- Do not introduce dependencies unless required for the task
- Validate at system boundaries only (user input, external APIs)
- When in doubt about a destructive or irreversible action, ask the user first

## Testing

No test framework is configured. When adding tests:
- Choose a framework appropriate for the project stack
- Document the test command in this file and in `README.md`
- Ensure tests pass before committing

## Linting and Formatting

No linters or formatters are configured. When adding them:
- Document the commands here
- Add configuration files appropriate for the stack
- Run linting before committing

## Future Updates

Update this file as the project evolves to reflect:
- Project purpose and architecture
- Dependency management and install commands
- Build and run commands
- Test commands
- Linting and formatting commands
- Deployment workflow
