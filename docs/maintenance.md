# Maintenance and releases

## Compatibility matrix

| Component | Supported |
| --- | --- |
| Operating systems | Windows and Linux |
| Python | 3.11, 3.12, 3.13 |
| CI coverage | Each supported Python version on Windows and Linux |
| Dependencies | Python standard library for the checked-in gateway |

## Versioning

Use Semantic Versioning. Patch releases fix defects without changing the public CLI or JSON contract. Minor releases add backward-compatible behavior. Major releases are required for incompatible CLI, envelope, schema, or safety-boundary changes. Before `1.0.0`, document all interface changes prominently in the changelog.

## Release process

1. Ensure CI is green for the target commit.
2. Update `CHANGELOG.md`, documentation, and schemas for user-visible changes.
3. Create and push an annotated tag named `vMAJOR.MINOR.PATCH` from the reviewed commit.
4. The release workflow re-runs compile and evaluation checks, then creates GitHub release notes from merged pull requests using `.github/release.yml`.
5. Verify the generated notes and release assets; publish a corrective follow-up release rather than editing history if a defect is found.

## Security and dependency updates

Treat workflow actions and Python/runtime changes as supply-chain changes. Pin GitHub Actions to immutable commit SHAs, review provenance and release notes before updating pins, and test the complete CI matrix after an update. Review dependency and action updates at least monthly and promptly after a credible security advisory. Use GitHub private vulnerability reporting for security issues.

## Routine maintenance

At least quarterly, review issue templates, CODEOWNERS, supported Python versions, and the documentation examples. Confirm that public examples remain sanitized and that generated indexes, reports, local environments, and secrets stay ignored.
