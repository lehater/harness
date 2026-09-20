import unittest
from lifecycle_experiment import evaluate_lifecycle_target

GRAPH={"version":1,"kind":"harness-engineering-graph","id":"X","authorities":[
{"id":"SOURCE","responsibility":"Source facts.","boundary":{"semantic_cohesion":"Source facts.","independent_change":"Source facts change independently.","public_contract":"Accepted source facts."},"produces":[{"capability":"source.identity","requires":[]},{"capability":"source.structure","requires":[]}]},
{"id":"USE","responsibility":"Use identity.","boundary":{"semantic_cohesion":"Use decisions.","independent_change":"Use decisions change independently.","public_contract":"Accepted use result."},"produces":[{"capability":"use.result","requires":["source.identity"]}]}
],"consumers":[{"id":"IMPLEMENTATION","purpose":"Implement accepted result.","requires":["use.result"]}]}
MODEL={"artifacts":[{"id":"SOURCE","authority":"SOURCE","path":"source.md","provides":["source.identity","source.structure"],"depends_on":[]},{"id":"USE","authority":"USE","path":"use.md","provides":["use.result"],"depends_on":["SOURCE"]}],"questions":[]}

def projection(identity="ID1",structure="S1",accepted="ID1"):
    return {"version":1,"kind":"harness-capability-lifecycle","providers":[
      {"artifact":"SOURCE","capability":"source.identity","revision":identity,"accepted_prerequisites":{}},
      {"artifact":"SOURCE","capability":"source.structure","revision":structure,"accepted_prerequisites":{}},
      {"artifact":"USE","capability":"use.result","revision":"U1","accepted_prerequisites":{"source.identity":accepted}}]}

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
if __name__=="__main__": unittest.main()
