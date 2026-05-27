# rielflow fixture package registry

This repository contains fixture workflow packages for rielflow package command testing.

Packages:

- fixture-clean-workflow: valid package for successful search and checkout.
- fixture-prompt-injection-workflow: contains prompt-injection text for reject-mode pre-install checks.
- fixture-credential-exfiltration-workflow: contains credential-exfiltration text for warn/reject pre-install checks.
- fixture-integrity-mismatch-workflow: intentionally incorrect md5/sha256 manifest metadata.
- fixture-invalid-metadata-workflow: intentionally invalid structured workflow metadata.

The package data is intentionally synthetic and should not be used as production workflow content.
