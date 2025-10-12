# Contributing to Toyfoundry

Thank you for helping build Toyfoundry’s manufacturing pipeline. This guide outlines how to propose improvements, document production doctrine, and keep our safety rails intact.

## Getting Started

1. **Review Doctrine** – Read the planning scrolls in `planning/`, especially `toyfoundry/` and `command_exchange_protocol.md`, to understand current manufacturing workflows.
2. **Sync the Exchange** – Pull the `exchange/` submodule to view the latest orders, acknowledgements, and production reports.
3. **Set Up Tooling** – Install any required Forge or validation utilities referenced in `planning/forge_automation_spec.md`.

## Contribution Workflow

1. **Open an Issue or RFO** – Describe the manufacturing change you propose. Include affected batches, safety considerations, and telemetry impacts.
2. **Create a Branch** – Use a descriptive branch name (e.g., `feature/batch-telemetry-updates`).
3. **Make Focused Changes** – Update only the files necessary for your change. Include rationale in doc comments when automation behaviour is complex.
4. **Verify Safety Rails** – Run validators, tests, and linting. Ensure manufacturing metrics and schemas stay compliant.
5. **Document the Update** – Add entries to `planning/change_log.md` and reference any relevant orders or ledger notes.
6. **Submit a Pull Request** – Summarize the change, testing performed, and manufacturing implications. Request review from governance stewards when the update affects safety critical components.

## Review Expectations

- Reviewers evaluate accuracy, safety, and clarity. They may request additional telemetry, tests, or documentation.
- Contributors should respond quickly to feedback and keep discussions respectful and grounded in doctrine.
- Significant changes to rituals, safety rails, or exchange automation require sign-off from Toyfoundry governance before merge.

## Release Process

- When a change is approved, merge commits should reference the tracking order ID from the exchange.
- After merge, update the exchange ledger with new production capabilities or manufacturing notes if required by the governing order.
- Coordinate with toysoldiers teams before distributing new Alfa batches or automation scripts.

By contributing, you affirm that you will maintain Toyfoundry’s manufacturing standards, respect the Code of Conduct, and keep safety as the top priority.
