"""
Automated Test Suite for BCSFE Web Application
Tests all save manipulation features and verifies data integrity.
"""

import unittest
from bcsfe_service import service
from bcsfe import core

class TestBcsfeWeb(unittest.TestCase):
    def setUp(self):
        # Create a fresh test save for each test
        self.status = service.create_test_save(cc_str="tw", gv_str="14.2.0")

    def test_01_create_test_save(self):
        self.assertTrue(service.has_save())
        self.assertEqual(self.status["cc"], "tw")
        self.assertEqual(self.status["game_version"], "14.2.0")
        self.assertEqual(self.status["catfood"], 1000)
        self.assertEqual(self.status["xp"], 100000)
        print("  [PASS] test_01_create_test_save")

    def test_02_edit_currencies(self):
        res = service.edit_currencies({
            "catfood": 19999,
            "xp": 99999999,
            "leadership": 999,
            "normal_tickets": 888,
            "rare_tickets": 99,
            "platinum_tickets": 9,
            "legend_tickets": 9,
            "np": 9999,
        })
        self.assertEqual(res["catfood"], 19999)
        self.assertEqual(res["xp"], 99999999)
        self.assertEqual(res["leadership"], 999)
        self.assertEqual(res["normal_tickets"], 888)
        self.assertEqual(res["rare_tickets"], 99)
        self.assertEqual(res["platinum_tickets"], 9)
        self.assertEqual(res["legend_tickets"], 9)
        self.assertEqual(res["np"], 9999)
        print("  [PASS] test_02_edit_currencies")

    def test_03_edit_battle_items(self):
        res = service.edit_battle_items({"all_amount": 999, "golden_cpu_count": 99})
        self.assertEqual(res["golden_cpu_count"], 99)
        for item in res["battle_items"]:
            self.assertEqual(item["amount"], 999)
        print("  [PASS] test_03_edit_battle_items")

    def test_04_edit_catfruit_and_eyes(self):
        res_cf = service.edit_catfruit({"all_amount": 128})
        for item in res_cf["catfruit"]:
            self.assertEqual(item["amount"], 128)

        res_ce = service.edit_catseyes({"all_amount": 99})
        for item in res_ce["catseyes"]:
            self.assertEqual(item["amount"], 99)

        res_ca = service.edit_catamins({"all_amount": 999})
        for item in res_ca["catamins"]:
            self.assertEqual(item["amount"], 999)
        print("  [PASS] test_04_edit_catfruit_and_eyes")

    def test_05_edit_cats(self):
        res = service.edit_cats({
            "unlock_all": True,
            "upgrade_level": {"base": 50, "plus": 90},
            "unlock_true_form": True,
            "unlock_fourth_form": True,
            "max_talents": True,
            "unlock_guide": True,
        })
        self.assertGreater(res["cats_unlocked"], 0)
        self.assertEqual(res["cats_unlocked"], res["cats_total"])
        print(f"  [PASS] test_05_edit_cats (Unlocked {res['cats_unlocked']} cats)")

    def test_06_edit_stages(self):
        res = service.edit_stages({
            "clear_story": True,
            "all_gold_treasures": True,
            "max_timed_scores": True,
            "clear_outbreaks": True,
            "unlock_aku": True,
            "clear_aku": True,
            "clear_sol": True,
            "clear_ul": True,
            "clear_zl": True,
            "clear_towers": True,
        })
        self.assertTrue(res["loaded"])
        # Verify gold treasures in story chapters
        for ch in service.save_file.story.get_real_chapters():
            for st in ch.get_valid_treasure_stages():
                self.assertEqual(st.treasure, 3)
        print("  [PASS] test_06_edit_stages (All Gold Treasures verified)")

    def test_07_edit_base_and_gamatoto(self):
        res = service.edit_gamatoto_and_base({
            "max_gamatoto": True,
            "legendary_helpers": True,
            "base_materials_amount": 9999,
            "max_engineers": True,
            "unlock_max_cannons": True,
            "max_cat_shrine": True,
            "max_special_skills": True,
        })
        self.assertEqual(res["engineers"], 5)
        for mat in res["base_materials"]:
            self.assertEqual(mat["amount"], 9999)
        print("  [PASS] test_07_edit_base_and_gamatoto")

    def test_08_edit_fixes_and_extras(self):
        res = service.edit_fixes_and_extras({
            "fix_time": True,
            "fix_gamatoto": True,
            "fix_ototo": True,
            "fix_officer_pass": True,
            "unlock_lineups": True,
            "unlock_medals": True,
            "clear_missions": True,
            "unlock_enemy_guide": True,
            "unlock_gold_pass": True,
            "reset_gambling": True,
            "playtime_hours": 200,
        })
        self.assertTrue(res["loaded"])
        print("  [PASS] test_08_edit_fixes_and_extras")

    def test_09_export_and_reload(self):
        # Apply edits
        service.apply_one_click(safe_mode=True)
        exported_bytes = service.export_bytes()
        self.assertGreater(len(exported_bytes), 1000)

        # Reload into a new service instance
        service2 = service.__class__()
        reloaded_status = service2.load_from_bytes(exported_bytes, cc_str="tw")
        self.assertEqual(reloaded_status["catfood"], 19999)
        self.assertEqual(reloaded_status["xp"], 99999999)
        self.assertEqual(reloaded_status["leadership"], 9999)
        self.assertEqual(reloaded_status["cats_unlocked"], reloaded_status["cats_total"])
        print("  [PASS] test_09_export_and_reload (Data serialized and re-parsed cleanly)")


if __name__ == "__main__":
    print("=== Running BCSFE Web Test Suite ===")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBcsfeWeb)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if not result.wasSuccessful():
        exit(1)
