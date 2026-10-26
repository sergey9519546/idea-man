"""Task-content checks for broad workflows; no model-quality claims."""
import unittest
from test_router_v2 import assessment, router

class TaskContentRubricTests(unittest.TestCase):
    def test_business_diagnosis_is_analysis_not_strategy_pitch(self):
        plan=router.plan_v2(assessment(domain='business',actions=['diagnose'],
            artifact_kind='analysis'))
        self.assertEqual(plan['rubric'],'analysis')

    def test_process_document_checks_process_not_only_presentation(self):
        plan=router.plan_v2(assessment(domain='operations',actions=['develop'],
            deliverable='document',artifact_kind='process',
            capabilities=['document_authoring']))
        self.assertEqual(plan['rubric'],'process')

    def test_engineering_defaults_to_analysis_unless_code_is_requested(self):
        self.assertEqual(router.registry()['domain_rubrics']['engineering'],'analysis')
        for domain in ['engineering','operations','business']:
            with self.subTest(domain=domain):
                plan=router.plan_v2(assessment(domain=domain,actions=['produce'],
                    deliverable='code',delivery_mode='inline',artifact_kind='analysis'))
                self.assertEqual(plan['rubric'],'code')

    def test_same_topic_can_require_a_different_completion_standard(self):
        for artifact,expected in [('analysis','analysis'),('decision_memo','decision'),
                                  ('experiment_plan','experiment'),('process','process')]:
            with self.subTest(artifact=artifact):
                plan=router.plan_v2(assessment(domain='business',actions=['review'],
                    deliverable='document',artifact_kind=artifact,
                    capabilities=['document_authoring']))
                self.assertEqual(plan['rubric'],expected)

    def test_media_and_unknown_artifacts_keep_applicable_checks(self):
        for deliverable,capability,expected in [('image','image_generation','visual'),
                                                ('deck','deck_authoring','presentation')]:
            plan=router.plan_v2(assessment(domain='general',actions=['produce'],
                artifact_kind='unspecified_pack',deliverable=deliverable,
                capabilities=[capability]))
            self.assertEqual(plan['rubric'],expected)

if __name__=='__main__':unittest.main()
