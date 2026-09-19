.PHONY: harness-check

harness-check:
	python validators/validate_core.py
	python validators/validate_adapters.py
	python validators/validate_target_state.py
	python validators/validate_workspace.py
	python validators/validate_agent_layer.py
