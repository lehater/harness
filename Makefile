.PHONY: harness-check assurance-fast assurance-full assurance-external-release assurance-external-release-plan

assurance-fast:
	python -m harness.assurance.execution_profiles fast

assurance-full:
	python -m harness.assurance.execution_profiles full

assurance-external-release:
	python -m harness.assurance.execution_profiles external-release

assurance-external-release-plan:
	python -m harness.assurance.execution_profiles external-release --plan

harness-check:
	python checks/validate_ci_policy.py
	python checks/validate_assurance_registry.py
	python checks/validate_prep_harness_regression_matrix.py
	python checks/validate_cross_project_portability.py
	python tests/test_behavioral_eval.py
	python tests/test_behavioral_eval_cases.py
	python checks/validate_context_boundaries.py
	python tests/test_core.py
	python tests/test_adapters.py
	python tests/test_target_state.py
	python tests/test_engineering_graph.py
	python checks/validate_authority_catalog.py
	python checks/validate_authority_boundary_research.py
	python checks/validate_ddd_authority_research.py
	python checks/validate_reference_applicability_research.py
	python tests/test_reference_engineering_model.py
	python tests/test_reference_model_evolution.py
	python tests/test_specialization_proof_semantics.py
	python checks/validate_project_behavior_evals.py
	python checks/validate_project_engineering_status.py
	python tests/test_project_status_e2e.py
	python tests/test_agent_router.py
	python tests/test_workspace.py
	python checks/validate_agent_layer.py
	python checks/validate_instruction_ownership.py
	python tests/test_skill_router.py
	python tests/test_fresh_context_routing.py
	python tests/test_method_router.py
	python tests/test_source_coverage.py
	python tests/test_user_facing_application.py
	python tests/test_frontend_screen_contracts.py
	python tests/test_frontend_ux_closure.py
	python tests/test_unified_model.py
	python tests/test_graph_doctor.py
	python tests/test_human_projection.py
	python tests/test_structurizr_projection.py
	python tests/test_dbml_projection.py
	python tests/test_application_process_bpmn_projection.py
	python tests/test_coverage_map_experiment.py
	python tests/test_coverage_derivation_experiment.py
	python tests/test_coverage_planner_experiment.py
	python checks/validate_concern_proof_model.py
	python tests/test_engineering_graph_semantic_claims_experiment.py
	python checks/validate_concern_activation_policy.py
	python tests/test_concern_activation_experiment.py
	python tests/test_coverage_control_loop_experiment.py
	python tests/test_concern_activation_scaling.py
	python tests/test_authority_role_projection_experiment.py
	python tests/test_consumer_scoped_activation.py
	python tests/test_consumer_scoped_coverage_proof.py
	python tests/test_intra_consumer_scope.py
	python tests/test_subject_scoped_coverage.py
	python tests/test_subject_obligations.py
	python tests/test_engineering_coverage.py
	python tests/test_repository_realization_design.py
	python tests/test_test_realization_conformance.py
	python tests/test_traceability_projection.py
	python tests/test_architecture_driver_closure.py
	python tests/test_coverage_blocker_transition.py
	python tests/test_coverage_production_contract_overlay.py
	python tests/test_semantic_acceptance.py
	python tests/test_application_process_design.py
	python checks/validate_skill_invariant_policy.py
	python tests/test_capability_lifecycle.py
	python tests/test_deep_dependency_graphs.py
	python tests/test_decision_governance.py
	python tests/test_decision_pipeline.py
	python tests/test_project_frontier.py
	python tests/test_reconciliation.py
	python tests/test_project_publication.py
	python tests/test_derivation_composition.py
	python tests/test_semantic_admission.py
	python tests/test_semantic_question_loop.py
	python tests/test_semantic_closure.py
	python checks/validate_harness.py
	python -m unittest tests/test_lifecycle_experiment.py
	python tests/test_assurance_execution_profiles.py
	python tests/test_consumer_api_compatibility.py
	python tests/test_consumer_pack.py
	python tests/test_consumer_wrapper.py
	python tests/test_scenario_suite.py
	python tests/test_dependency_resolution_calibration.py
	python tests/test_dependency_resolution_holdout.py
	python tests/test_dependency_resolution_grounding.py
	python tests/test_dependency_resolution_project_snapshot.py
	python tests/test_dependency_resolution_directness.py
	python tests/test_dependency_resolution_target_readiness.py
	python tests/test_dependency_resolution_target_scope_coverage.py
	python tests/test_dependency_resolution_responsibility_routing.py
	python tests/test_dependency_resolution_claim_mapping.py
	python tests/test_dependency_resolution_strategy_claim_review.py
	python tests/test_dependency_resolution_target_semantic_audit.py
	python tests/test_dependency_resolution_target_obligation_revision.py
	python tests/test_cdr_operational.py
	python tests/test_cdr_contract_change.py
	python tests/test_cdr_reference_audit.py
	python tests/test_cdr_reference_provider_pilot.py
	python tests/test_cdr_direction_holdout.py
	python tests/test_dependency_resolution_process_driver.py
	python tests/test_copilot_dependency_resolution_evaluator.py
	python tests/test_live_calibration_process_driver.py
	python tests/test_copilot_live_calibration_evaluator.py

# Explicit operator invocation only. Never part of harness-check or the
# Capability creation route until independently approved governance exists.
.PHONY: cdr-prepare cdr-reconcile cdr-audit
cdr-prepare:
	@test -n "$(PROJECT_ROOT)" -a -n "$(PROJECT_COMMIT)" -a -n "$(CDR_INTAKE)" -a -n "$(CDR_OUTPUT)" || (echo "Require PROJECT_ROOT PROJECT_COMMIT CDR_INTAKE CDR_OUTPUT"; exit 2)
	python -m evals.cdr_operational prepare --project-root "$(PROJECT_ROOT)" --commit "$(PROJECT_COMMIT)" --intake "$(CDR_INTAKE)" --output "$(CDR_OUTPUT)"

cdr-reconcile:
	@test -n "$(PROJECT_ROOT)" -a -n "$(PROJECT_COMMIT)" -a -n "$(CDR_INTAKE)" -a -n "$(CDR_PREDICTIONS)" -a -n "$(CDR_OUTPUT)" || (echo "Require PROJECT_ROOT PROJECT_COMMIT CDR_INTAKE CDR_PREDICTIONS CDR_OUTPUT"; exit 2)
	python -m evals.cdr_operational reconcile --project-root "$(PROJECT_ROOT)" --commit "$(PROJECT_COMMIT)" --intake "$(CDR_INTAKE)" --predictions "$(CDR_PREDICTIONS)" --output "$(CDR_OUTPUT)"

cdr-audit:
	@test -n "$(PROJECT_ROOT)" -a -n "$(PROJECT_COMMIT)" -a -n "$(CDR_OUTPUT)" || (echo "Require PROJECT_ROOT PROJECT_COMMIT CDR_OUTPUT"; exit 2)
	python -m evals.cdr_graph_audit --project-root "$(PROJECT_ROOT)" --commit "$(PROJECT_COMMIT)" --output "$(CDR_OUTPUT)"

# Decision-review preparation remains nonauthorizing. Even complete reviewer
# drafts do not approve Engineering Graph mutation or bypass Authority policy.
.PHONY: cdr-dossier cdr-check-review
cdr-dossier:
	@test -n "$(PROJECT_ROOT)" -a -n "$(PROJECT_COMMIT)" -a -n "$(CDR_INTAKE)" -a -n "$(CDR_PREDICTIONS)" -a -n "$(CDR_OUTPUT)" || (echo "Require PROJECT_ROOT PROJECT_COMMIT CDR_INTAKE CDR_PREDICTIONS CDR_OUTPUT"; exit 2)
	python -m evals.cdr_governance_packet prepare --project-root "$(PROJECT_ROOT)" --commit "$(PROJECT_COMMIT)" --intake "$(CDR_INTAKE)" --predictions "$(CDR_PREDICTIONS)" --output "$(CDR_OUTPUT)"

cdr-check-review:
	@test -n "$(PROJECT_ROOT)" -a -n "$(PROJECT_COMMIT)" -a -n "$(CDR_INTAKE)" -a -n "$(CDR_PREDICTIONS)" -a -n "$(CDR_DOSSIER)" -a -n "$(CDR_REVIEW)" -a -n "$(CDR_OUTPUT)" || (echo "Require PROJECT_ROOT PROJECT_COMMIT CDR_INTAKE CDR_PREDICTIONS CDR_DOSSIER CDR_REVIEW CDR_OUTPUT"; exit 2)
	python -m evals.cdr_governance_packet check-draft --project-root "$(PROJECT_ROOT)" --commit "$(PROJECT_COMMIT)" --intake "$(CDR_INTAKE)" --predictions "$(CDR_PREDICTIONS)" --dossier "$(CDR_DOSSIER)" --review "$(CDR_REVIEW)" --output "$(CDR_OUTPUT)"

# Explicit read-only project contract-change reconsideration; Lifecycle retains
# accepted-semantic currentness and graph changes remain Authority governed.
.PHONY: cdr-change-preflight
cdr-change-preflight:
	@test -n "$(PROJECT_ROOT)" -a -n "$(CDR_BEFORE)" -a -n "$(PROJECT_COMMIT)" -a -n "$(CDR_OUTPUT)" || (echo "Require PROJECT_ROOT CDR_BEFORE PROJECT_COMMIT CDR_OUTPUT"; exit 2)
	python -m evals.cdr_contract_change --project-root "$(PROJECT_ROOT)" --before "$(CDR_BEFORE)" --after "$(PROJECT_COMMIT)" --output "$(CDR_OUTPUT)"

# Reference Model is research-only; source-only Phase A and graph-aware Phase B
# are intentionally distinct and neither can mutate a project graph.
.PHONY: cdr-reference-prepare cdr-reference-audit
cdr-reference-prepare:
	@test -n "$(CDR_OUTPUT)" || (echo "Require CDR_OUTPUT"; exit 2)
	python -m evals.cdr_reference_audit prepare --output "$(CDR_OUTPUT)"

cdr-reference-audit:
	@test -n "$(CDR_OUTPUT)" || (echo "Require CDR_OUTPUT"; exit 2)
	python -m evals.cdr_reference_audit audit --output "$(CDR_OUTPUT)"
