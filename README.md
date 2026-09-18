# Harness

Repository-independent operating model for AI-assisted engineering work.

Harness defines reusable methodology and generic Skills. Target project repositories independently own product/domain truth, architecture, decisions, implementation constraints and durable execution state.

Core boundary:

```text
Harness = how work is performed
Project = what is true, what is active, and what is authorized
```

There is no required binding, manifest, pin or runtime coupling between Harness and a target project. In a chat/session, the user may instruct the agent to use this Harness while working on any repository. The agent reads only the relevant Harness material and the relevant target-project material for that task.

Conversation history is not durable project state; resumable project state remains in the target repository.

