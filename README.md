# Harness

Repository-independent operating model for AI-assisted engineering work.

Harness defines reusable methodology, routing, Skills, project contracts, validation and evaluation mechanics. Product/domain truth and durable execution state remain in each target project repository.

Core boundary:

```text
Harness = how work is performed
Project = what is true, what is active, and what is authorized
```

A target project should be recoverable from its own repository plus a pinned Harness revision; conversational state is never required for recovery.

## Bootstrap

This commit only establishes the repository and ownership boundary. Further Harness development is performed on branches and integrated through pull requests with squash merge.
