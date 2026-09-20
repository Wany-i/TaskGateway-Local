## Summary

Describe the user-visible outcome and why it is needed.

## Validation

- [ ] `python -m compileall -q src`
- [ ] `python src/eval.py`
- [ ] Documentation and schemas updated where applicable

## Safety and compatibility

- [ ] No credentials, private paths, resource indexes, logs, or personal data are included.
- [ ] The change preserves fail-closed behavior and does not add hidden execution.
- [ ] Breaking CLI or JSON contract changes are called out in `CHANGELOG.md`.
