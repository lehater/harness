import unittest
from harness import CoreError
from lifecycle_experiment import evaluate_lifecycle_target, validate_projection

GRAPH={"version":1,"kind":"harness-engineering-graph","id":"X","authorities":[
{"id":"SOURCE","responsibility":"Source facts.","boundary":{"semantic_cohesion":"Source facts.","independent_change":"Source facts change independently.","public_contract":"Accepted source facts."},"produces":[{"capability":"source.identity","requires":[]},{"capability":"source.structure","requires":[]}]},
{"id":"USE","responsibility":"Use identity.","boundary":{"semantic_cohesion":"Use decisions.","independent_change":"Use decisions change independently.","public_contract":"Accepted use result."},"produces":[{"capability":"use.result","requires":["source.identity"]}]}
],"consumers":[{"id":"IMPLEMENTATION","purpose":"Implement accepted result.","requires":["use.result"]}]}
MODEL={"artifacts":[{"id":"SOURCE","authority":"SOURCE","path":"source.md","provides":["source.identity","source.structure"],"depends_on":[]},{"id":"USE","authority":"USE","path":"use.md","provides":["use.result"],"depends_on":["SOURCE"]}],"questions":[]}

def projection(identity="ID1",structure="S1",accepted="ID1"):
    return {"version":1,"kind":"harness-capability-lifecycle","providers":[
      {"artifact":"SOURCE","capability":"source.identity","acceptance_id":identity,"accepted_prerequisites":{}},
      {"artifact":"SOURCE","capability":"source.structure","acceptance_id":structure,"accepted_prerequisites":{}},
      {"artifact":"USE","capability":"use.result","acceptance_id":"U1","accepted_prerequisites":{"source.identity":accepted}}]}

class LifecycleExperimentTest(unittest.TestCase):
    def test_current_chain_is_complete(self):
        self.assertEqual("COMPLETE",evaluate_lifecycle_target(GRAPH,"IMPLEMENTATION",MODEL,projection())["status"])
    def test_unconsumed_capability_revision_does_not_invalidate(self):
        self.assertEqual("COMPLETE",evaluate_lifecycle_target(GRAPH,"IMPLEMENTATION",MODEL,projection(structure="S2"))["status"])
    def test_consumed_capability_revision_invalidates(self):
        r=evaluate_lifecycle_target(GRAPH,"IMPLEMENTATION",MODEL,projection(identity="ID2"))
        self.assertEqual("READY",r["status"]); self.assertEqual("use.result",r["revalidate"][0]["capability"])
    def test_revalidation_restores_complete(self):
        self.assertEqual("COMPLETE",evaluate_lifecycle_target(GRAPH,"IMPLEMENTATION",MODEL,projection(identity="ID2",accepted="ID2"))["status"])
    def test_missing_lifecycle_assertion_is_not_revalidate(self):
        p=projection(); p["providers"]=[x for x in p["providers"] if x["capability"]!="use.result"]
        r=evaluate_lifecycle_target(GRAPH,"IMPLEMENTATION",MODEL,p)
        self.assertEqual("INCOMPLETE",r["status"]); self.assertEqual([],r["revalidate"]); self.assertEqual("use.result",r["lifecycle_gaps"][0]["capability"])
    def test_missing_required_baseline_is_rejected(self):
        p=projection(); p["providers"][-1]["accepted_prerequisites"]={}
        with self.assertRaises(CoreError): validate_projection(GRAPH,MODEL,p)
    def test_extra_baseline_edge_is_rejected(self):
        p=projection(); p["providers"][-1]["accepted_prerequisites"]["source.structure"]="S1"
        with self.assertRaises(CoreError): validate_projection(GRAPH,MODEL,p)
    def test_duplicate_capability_assertion_is_rejected(self):
        p=projection(); p["providers"].append(dict(p["providers"][0]))
        with self.assertRaises(CoreError): validate_projection(GRAPH,MODEL,p)
    def test_capability_outside_production_topology_is_rejected(self):
        g={**GRAPH,"authorities":[*GRAPH["authorities"]]}
        m={"artifacts":[*MODEL["artifacts"],{"id":"EXTRA","authority":"USE","path":"extra.md","provides":["extra.capability"],"depends_on":[]}],"questions":[]}
        p=projection(); p["providers"].append({"artifact":"EXTRA","capability":"extra.capability","acceptance_id":"E1","accepted_prerequisites":{}})
        with self.assertRaises(CoreError): validate_projection(g,m,p)
    def test_assertion_must_match_core_provider(self):
        p=projection(); p["providers"][0]["artifact"]="USE"
        with self.assertRaises(CoreError): validate_projection(GRAPH,MODEL,p)
if __name__=="__main__": unittest.main()
