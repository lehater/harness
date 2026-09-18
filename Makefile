.PHONY: harness-check

harness-check:
	python validators/validate_core.py
	python validators/validate_adapters.py
	python validators/validate_consumers.py
