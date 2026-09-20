# Contributing

Thanks for improving TaskGateway-Local. Contributions should preserve its core properties: deterministic results, explicit authorization boundaries, and no hidden side effects.

## Before opening a pull request

1. Open an issue for a material behavior or interface change before implementing it.
2. Keep changes small and focused; include tests or evaluation coverage for behavior changes.
3. Do not add real resource indexes, local paths, credentials, logs, or personal data to the repository.
4. Preserve fail-closed behavior. A missing, disabled, or unauthorized resource must not be silently substituted.

## Local checks

Use a supported Python version and run:

```powershell
python -m pip install -e ".[mcp,test]"
python -m compileall -q src
python -m pytest -q
```

Run the focused evaluation command when changing a related contract or command. Update `CHANGELOG.md` under `Unreleased` for user-visible changes.

## Pull request expectations

- Explain the problem, approach, and compatibility impact.
- Update schemas and documentation with public interface changes.
- Do not weaken validation just to make an example pass.
- Use conventional, imperative commit subjects where practical.

Maintainers may request a design discussion or split unrelated changes before review.
