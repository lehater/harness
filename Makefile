.PHONY: harness-check

harness-check:
	python validators/validate_core.py
	python validators/validate_adapters.py
	python validators/validate_target_state.py
	python validators/validate_engineering_graph.py
	python validators/validate_authority_catalog.py
	python validators/validate_agent_router.py
	python validators/validate_workspace.py
	python validators/validate_agent_layer.py
	python validators/validate_source_coverage.py
	python validators/validate_frontend_blind_pilot.py
