# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2026-09-20

### Fixed

- Blocked `invoke` responses now explicitly report `executed: false`.

## [1.0.0] - 2026-09-20

### Added

- Dependency-free TaskGateway core with read-first `search`, bounded `plan`, and non-executing `invoke`.
- Universal STDIO MCP server with three structured, read-only tools.
- Portable WorkBuddy local-marketplace plugin and reversible installer.
- MIT license, contribution/security policies, issue templates, CI, and tagged release workflow.
