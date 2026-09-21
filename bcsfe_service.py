"""
BCSFE Service Wrapper for Battle Cats Web Application
Provides seamless interfacing with the bcsfe library for save file operations.
Supports both stateful local servers and stateless serverless (Vercel) deployments.
"""

import base64
import datetime
from typing import Any, Dict, List, Optional, Tuple
from bcsfe import core

# Initialize core data
try:
    core.core_data.init_data()
except Exception as e:
    print(f"Warning initializing bcsfe core data: {e}")

# Monkey-patch SaveFile.unlock_equip_menu to avoid IndexError on modern game versions
def safe_unlock_equip_menu(self):
    if hasattr(self, "menu_unlocks") and len(self.menu_unlocks) > 2:
        self.menu_unlocks[2] = max(self.menu_unlocks[2], 1)

core.SaveFile.unlock_equip_menu = safe_unlock_equip_menu


class BcsfeService:
    def __init__(self):
        self.save_file: Optional[core.SaveFile] = None

    def has_save(self) -> bool:
        return self.save_file is not None

    def resolve_save(self, data: Optional[Dict[str, Any]] = None) -> Tuple[core.SaveFile, bool]:
        """Resolves the SaveFile to use, supporting stateless base64 input for serverless."""
        if data and "save_data" in data and data["save_data"]:
            raw_bytes = base64.b64decode(data["save_data"])
            cc_str = data.get("cc")
            cc = core.CountryCode.from_code(cc_str.lower()) if cc_str else None
            sf = core.SaveFile(dt=core.Data(raw_bytes), cc=cc)
            return sf, True
        if self.save_file is not None:
            return self.save_file, False
        raise ValueError("No save file loaded. Please create a test save or upload a save file first.")

    def pack_result(self, sf: core.SaveFile, is_stateless: bool) -> Dict[str, Any]:
        """Packs the response with updated status and base64 save_data."""
        status = self.get_status(sf)
        try:
            b64_str = base64.b64encode(sf.to_data().to_bytes()).decode("utf-8")
            status["save_data"] = b64_str
        except Exception as e:
            print(f"Warning encoding save_data base64: {e}")
        self.save_file = sf
        return status

    def create_test_save(self, cc_str: str = "tw", gv_str: str = "14.2.0") -> Dict[str, Any]:
        """Creates a fresh test save file with populated cats."""
        cc = core.CountryCode.from_code(cc_str.lower())
        gv = core.GameVersion.from_string(gv_str)
        self.save_file = core.SaveFile(load=False, cc=cc, gv=gv)
        self.save_file.init_save(gv)
        self.save_file.inquiry_code = "TEST_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.save_file.catfood = 1000
        self.save_file.xp = 100000
        self.save_file.leadership = 10

        # Populate cats
        try:
            total_cats = len(core.UnitBuy(self.save_file).unit_buy)
            cats_list = [core.Cat.init(i) for i in range(total_cats)]
            self.save_file.cats = core.Cats(cats_list)
        except Exception as e:
            print(f"Warning populating cats: {e}")

        return self.pack_result(self.save_file, False)

    def load_from_bytes(self, data: bytes, cc_str: Optional[str] = None) -> Dict[str, Any]:
        """Loads a save file from raw bytes."""
        core_data = core.Data(data)
        cc = core.CountryCode.from_code(cc_str.lower()) if cc_str else None
        self.save_file = core.SaveFile(dt=core_data, cc=cc)
        return self.pack_result(self.save_file, False)

    def export_bytes(self, save_data_b64: Optional[str] = None) -> bytes:
        """Exports the save file as encrypted bytes (from base64 or memory)."""
        if save_data_b64:
            return base64.b64decode(save_data_b64)
        if not self.save_file:
            raise ValueError("No save file loaded")
        return self.save_file.to_data().to_bytes()

    def download_from_server(
        self, transfer_code: str, confirmation_code: str, cc_str: str, gv_str: str = "14.2.0"
    ) -> Dict[str, Any]:
        """Downloads a save file from PONOS servers using transfer codes."""
        cc = core.CountryCode.from_code(cc_str.lower())
        gv = core.GameVersion.from_string(gv_str)
        server_handler, result = core.ServerHandler.from_codes(
            transfer_code=transfer_code,
            confirmation_code=confirmation_code,
            cc=cc,
            gv=gv,
            print=False,
            save_backup=False,
        )
        if server_handler is None or server_handler.save_file is None:
            err_msg = "Download failed from PONOS server. Please check transfer code, confirmation code, and region."
            if result and hasattr(result, "response") and result.response:
                err_msg += f" (HTTP {result.response.status_code})"
            raise RuntimeError(err_msg)

        self.save_file = server_handler.save_file
        return self.pack_result(self.save_file, False)

    def upload_to_server(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, str]:
        """Uploads the save file to PONOS server and retrieves transfer codes."""
        s, _ = self.resolve_save(data)
        server_handler = core.ServerHandler(s)
        codes = server_handler.get_codes()
        if not codes:
            raise RuntimeError("Failed to upload save to PONOS server. Server might have rejected the request or inquiry code.")
        transfer_code, confirmation_code = codes
        return {
            "transfer_code": transfer_code,
            "confirmation_code": confirmation_code,
        }

    def get_status(self, sf: Optional[core.SaveFile] = None) -> Dict[str, Any]:
        """Returns comprehensive information about the loaded save file."""
        s = sf or self.save_file
        if not s:
            return {"loaded": False}

        cc = s.cc.get_code() if s.cc else "unknown"
        gv = s.game_version.to_string() if s.game_version else "unknown"

        # User rank calculation
        user_rank = 0
        try:
            user_rank = s.calculate_user_rank()
        except Exception:
            user_rank = 0

        # Battle items
        battle_items = []
        item_names = ["速度加快", "寶物雷達", "土豪貓", "貓咪電腦", "洞悉先機", "狙擊手"]
        try:
            for i, item in enumerate(s.battle_items.items):
                name = item_names[i] if i < len(item_names) else f"道具 {i+1}"
                battle_items.append({
                    "id": i,
                    "name": name,
                    "amount": item.amount,
                    "locked": item.locked,
                })
        except Exception:
            pass

        # Catfruit
        catfruit_items = []
        try:
            cf_names = core.Matatabi(s).get_names() or []
            for i, val in enumerate(s.catfruit):
                name = cf_names[i] if i < len(cf_names) and cf_names[i] else f"貓薄荷/獸石 {i+1}"
                catfruit_items.append({"id": i, "name": name, "amount": val})
        except Exception:
            pass

        # Catseyes
        catseyes_items = []
        catseye_names = ["EX貓目石", "稀有貓目石", "激稀有貓目石", "超激稀有貓目石", "傳說貓目石", "暗黑貓目石"]
        try:
            for i, val in enumerate(s.catseyes):
                name = catseye_names[i] if i < len(catseye_names) else f"貓目石 {i+1}"
                catseyes_items.append({"id": i, "name": name, "amount": val})
        except Exception:
            pass

        # Catamins
        catamins_items = []
        catamin_names = ["喵力達 A", "喵力達 B", "喵力達 C"]
        try:
            for i, val in enumerate(s.catamins):
                name = catamin_names[i] if i < len(catamin_names) else f"喵力達 {i+1}"
                catamins_items.append({"id": i, "name": name, "amount": val})
        except Exception:
            pass

        # Base Materials
        base_materials = []
        material_names = ["紅磚", "羽毛", "煤炭", "鋼鐵齒輪", "黃金", "宇宙隕石", "古代獸骨", "菊石"]
        try:
            if hasattr(s.ototo, "base_materials") and hasattr(s.ototo.base_materials, "materials"):
                for i, mat in enumerate(s.ototo.base_materials.materials):
                    name = material_names[i] if i < len(material_names) else f"材料 {i+1}"
                    base_materials.append({"id": i, "name": name, "amount": mat.amount})
        except Exception:
            pass

        # Cats count
        unlocked_cats_count = 0
        total_cats_count = 0
        try:
            if hasattr(s.cats, "cats"):
                total_cats_count = len(s.cats.cats)
                unlocked_cats_count = sum(1 for c in s.cats.cats if getattr(c, "unlocked", 0) > 0)
        except Exception:
            pass

        # Gamatoto
        gamatoto_info = {"level": 0, "xp": getattr(s.gamatoto, "xp", 0), "helpers_count": 0}
        try:
            g_levels = core.core_data.get_gamatoto_levels(s)
            curr_lvl = g_levels.get_level_from_xp(s.gamatoto.xp)
            if curr_lvl:
                gamatoto_info["level"] = curr_lvl.level
            if hasattr(s.gamatoto, "helpers") and hasattr(s.gamatoto.helpers, "helpers"):
                gamatoto_info["helpers_count"] = sum(1 for h in s.gamatoto.helpers.helpers if h.is_valid())
        except Exception:
            pass

        # Playtime
        playtime_hours = 0
        try:
            playtime_hours = round(getattr(s, "timestamp", 0) / 3600, 1)
        except Exception:
            pass

        return {
            "loaded": True,
            "cc": cc,
            "game_version": gv,
            "inquiry_code": getattr(s, "inquiry_code", ""),
            "user_rank": user_rank,
            "catfood": getattr(s, "catfood", 0),
            "xp": getattr(s, "xp", 0),
            "leadership": getattr(s, "leadership", 0),
            "normal_tickets": getattr(s, "normal_tickets", 0),
            "rare_tickets": getattr(s, "rare_tickets", 0),
            "platinum_tickets": getattr(s, "platinum_tickets", 0),
            "legend_tickets": getattr(s, "legend_tickets", 0),
            "platinum_shards": getattr(s, "platinum_shards", 0),
            "np": getattr(s, "np", 0),
            "golden_cpu_count": getattr(s, "golden_cpu_count", 0),
            "hundred_million_ticket": getattr(s, "hundred_million_ticket", 0),
            "playtime_hours": playtime_hours,
            "cats_unlocked": unlocked_cats_count,
            "cats_total": total_cats_count,
            "battle_items": battle_items,
            "catfruit": catfruit_items,
            "catseyes": catseyes_items,
            "catamins": catamins_items,
            "base_materials": base_materials,
            "gamatoto": gamatoto_info,
            "engineers": getattr(s.ototo, "engineers", 0) if hasattr(s, "ototo") else 0,
        }

    # ==========================================
    # 1. CURRENCIES & BASIC ITEMS
    # ==========================================
    def edit_currencies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)

        if "catfood" in data:
            s.catfood = int(data["catfood"])
        if "xp" in data:
            s.xp = int(data["xp"])
        if "leadership" in data:
            s.leadership = int(data["leadership"])
        if "normal_tickets" in data:
            s.normal_tickets = int(data["normal_tickets"])
        if "rare_tickets" in data:
            s.rare_tickets = int(data["rare_tickets"])
        if "platinum_tickets" in data:
            s.platinum_tickets = int(data["platinum_tickets"])
        if "legend_tickets" in data:
            s.legend_tickets = int(data["legend_tickets"])
        if "platinum_shards" in data:
            s.platinum_shards = int(data["platinum_shards"])
        if "np" in data:
            s.np = int(data["np"])
        if "hundred_million_ticket" in data:
            s.hundred_million_ticket = int(data["hundred_million_ticket"])

        return self.pack_result(s, is_stateless)

    # ==========================================
    # 2. BATTLE ITEMS
    # ==========================================
    def edit_battle_items(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)

        amount = data.get("all_amount")
        if amount is not None:
            amt = int(amount)
            for item in s.battle_items.items:
                item.amount = amt
                item.locked = False
        else:
            items_list = data.get("items", [])
            for item_data in items_list:
                idx = item_data.get("id")
                amt = item_data.get("amount")
                if idx is not None and 0 <= idx < len(s.battle_items.items):
                    s.battle_items.items[idx].amount = int(amt)
                    s.battle_items.items[idx].locked = False

        if "golden_cpu_count" in data:
            s.golden_cpu_count = int(data["golden_cpu_count"])

        return self.pack_result(s, is_stateless)

    # ==========================================
    # 3. CATFRUIT, CATSEYES, CATAMINS
    # ==========================================
    def edit_catfruit(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)

        cf_names = core.Matatabi(s).get_names() or []
        count = max(len(s.catfruit), len(cf_names), 29)
        if len(s.catfruit) < count:
            s.catfruit.extend([0] * (count - len(s.catfruit)))

        all_amount = data.get("all_amount")
        if all_amount is not None:
            amt = int(all_amount)
            s.catfruit = [amt] * len(s.catfruit)
        elif "items" in data:
            for item in data["items"]:
                idx = item.get("id")
                amt = item.get("amount")
                if idx is not None and 0 <= idx < len(s.catfruit):
                    s.catfruit[idx] = int(amt)

        return self.pack_result(s, is_stateless)

    def edit_catseyes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)

        count = max(len(s.catseyes), 6)
        if len(s.catseyes) < count:
            s.catseyes.extend([0] * (count - len(s.catseyes)))

        all_amount = data.get("all_amount")
        if all_amount is not None:
            amt = int(all_amount)
            s.catseyes = [amt] * len(s.catseyes)
        elif "items" in data:
            for item in data["items"]:
                idx = item.get("id")
                amt = item.get("amount")
                if idx is not None and 0 <= idx < len(s.catseyes):
                    s.catseyes[idx] = int(amt)

        return self.pack_result(s, is_stateless)

    def edit_catamins(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)

        count = max(len(s.catamins), 3)
        if len(s.catamins) < count:
            s.catamins.extend([0] * (count - len(s.catamins)))

        all_amount = data.get("all_amount")
        if all_amount is not None:
            amt = int(all_amount)
            s.catamins = [amt] * len(s.catamins)
        elif "items" in data:
            for item in data["items"]:
                idx = item.get("id")
                amt = item.get("amount")
                if idx is not None and 0 <= idx < len(s.catamins):
                    s.catamins[idx] = int(amt)

        return self.pack_result(s, is_stateless)

    # ==========================================
    # 4. CATS & TALENTS
    # ==========================================
    def edit_cats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)
        cats = s.cats.cats

        unlock_all = data.get("unlock_all", False)
        rarities = data.get("rarities")
        upgrade_level = data.get("upgrade_level")
        unlock_true_form = data.get("unlock_true_form", False)
        unlock_fourth_form = data.get("unlock_fourth_form", False)
        max_talents = data.get("max_talents", False)
        unlock_guide = data.get("unlock_guide", False)

        talent_data = None
        if max_talents:
            try:
                talent_data = s.cats.read_talent_data(s)
            except Exception:
                pass

        for cat in cats:
            should_edit = False
            if unlock_all:
                cat.unlock(s)
                should_edit = True
            elif rarities is not None:
                try:
                    r = cat.get_rarity(s)
                    if r in rarities:
                        cat.unlock(s)
                        should_edit = True
                except Exception:
                    pass
            elif cat.unlocked > 0:
                should_edit = True

            if should_edit:
                if upgrade_level:
                    base = upgrade_level.get("base", -1)
                    plus = upgrade_level.get("plus", -1)
                    if base > 0:
                        cat.upgrade.base = base - 1
                    if plus >= 0:
                        cat.upgrade.plus = plus

                if unlock_true_form:
                    try:
                        cat.true_form(s, set_current_form=False)
                    except Exception:
                        pass

                if unlock_fourth_form:
                    try:
                        cat.unlock_fourth_form(s, set_current_form=False)
                    except Exception:
                        pass

                if max_talents and talent_data and cat.talents:
                    try:
                        t_data = talent_data.get_cat_talents(cat)
                        if t_data:
                            _, max_levels, _, ids = t_data
                            for i, tid in enumerate(ids):
                                t_obj = cat.get_talent_from_id(tid)
                                if t_obj and i < len(max_levels):
                                    t_obj.level = max_levels[i]
                    except Exception:
                        pass

                if unlock_guide:
                    try:
                        cat.nyanko_picture_book = 1
                    except Exception:
                        pass

        try:
            s.unlock_equip_menu()
        except Exception:
            pass

        return self.pack_result(s, is_stateless)

    # ==========================================
    # 5. STAGES & TREASURES
    # ==========================================
    def edit_stages(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)

        # Clear story chapters (EOC, ITF, COTC)
        if data.get("clear_story", False):
            try:
                for ch in s.story.get_real_chapters():
                    ch.clear_chapter()
                    for st in ch.stages:
                        st.clear_stage(1)
            except Exception as e:
                print(f"Error clearing story: {e}")

        # All gold treasures (100% gold for story chapters)
        if data.get("all_gold_treasures", False):
            try:
                for ch in s.story.get_real_chapters():
                    for st in ch.get_valid_treasure_stages():
                        st.set_treasure(3)
            except Exception as e:
                print(f"Error setting gold treasures: {e}")

        # Max ITF timed scores
        if data.get("max_timed_scores", False):
            try:
                for ch in s.story.get_real_chapters():
                    for st in ch.stages:
                        st.itf_timed_score = 9999
            except Exception as e:
                print(f"Error setting timed scores: {e}")

        # Clear Zombie outbreaks
        if data.get("clear_outbreaks", False):
            try:
                if hasattr(s, "outbreaks") and hasattr(s.outbreaks, "outbreaks"):
                    for ob in s.outbreaks.outbreaks:
                        if hasattr(ob, "stages"):
                            for st in ob.stages:
                                st.clear_times = 1
            except Exception as e:
                print(f"Error clearing outbreaks: {e}")

        # Aku Realm
        if data.get("unlock_aku", False) or data.get("clear_aku", False):
            try:
                if hasattr(s, "aku"):
                    s.aku.unlocked = True
                    if data.get("clear_aku", False):
                        if hasattr(s.aku, "chapters"):
                            for ch in s.aku.chapters:
                                if hasattr(ch, "stages"):
                                    for st in ch.stages:
                                        st.clear_stage(1)
            except Exception as e:
                print(f"Error editing aku realm: {e}")

        # Stories of Legend (SOL / 舊傳)
        if data.get("clear_sol", False):
            try:
                if hasattr(s, "event_stages"):
                    for group in getattr(s.event_stages, "chapters", []):
                        for ch in getattr(group, "chapters", []):
                            if hasattr(ch, "clear_map"):
                                for star in range(1, 5):
                                    ch.clear_map(0, star)
            except Exception as e:
                print(f"Error clearing SOL: {e}")

        # Uncanny Legends (UL / 真傳)
        if data.get("clear_ul", False):
            try:
                if hasattr(s, "uncanny") and hasattr(s.uncanny, "chapters"):
                    for ch_stars in getattr(s.uncanny.chapters, "chapters", []):
                        if hasattr(ch_stars, "chapters"):
                            for ch in ch_stars.chapters:
                                ch.chapter_unlock_state = 1
                                ch.clear_progress = 48
            except Exception as e:
                print(f"Error clearing UL: {e}")

        # Zero Legends (ZL / 零傳)
        if data.get("clear_zl", False):
            try:
                if hasattr(s, "zero_legends"):
                    for group in getattr(s.zero_legends, "chapters", []):
                        for ch in getattr(group, "chapters", []):
                            if hasattr(ch, "clear_map"):
                                ch.clear_map(0, 1)
            except Exception as e:
                print(f"Error clearing ZL: {e}")

        # Towers (Heavenly Tower & Infernal Tower)
        if data.get("clear_towers", False):
            try:
                if hasattr(s, "tower") and hasattr(s.tower, "chapters"):
                    for ch_stars in getattr(s.tower.chapters, "chapters", []):
                        if hasattr(ch_stars, "chapters"):
                            for ch in ch_stars.chapters:
                                ch.chapter_unlock_state = 1
                                ch.clear_progress = 50
            except Exception as e:
                print(f"Error clearing towers: {e}")

        return self.pack_result(s, is_stateless)

    # ==========================================
    # 6. BASE, GAMATOTO & OTOTO
    # ==========================================
    def edit_gamatoto_and_base(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)

        # Gamatoto Max Level / XP
        if data.get("max_gamatoto", False):
            try:
                g_levels = core.core_data.get_gamatoto_levels(s)
                max_lvl = g_levels.get_max_level()
                s.gamatoto.xp = g_levels.get_xp_from_level(max_lvl)
            except Exception as e:
                print(f"Error maxing gamatoto: {e}")

        # Gamatoto 10 Legendary Helpers
        if data.get("legendary_helpers", False):
            try:
                members_name = core.core_data.get_gamatoto_members_name(s)
                legendary_members = members_name.get_all_rarity(3) or []
                helpers = []
                for i in range(min(10, len(legendary_members))):
                    helpers.append(core.game.gamoto.gamatoto.Helper(legendary_members[i].member_id))
                s.gamatoto.helpers = core.game.gamoto.gamatoto.Helpers(helpers)
            except Exception as e:
                print(f"Error setting legendary helpers: {e}")

        # Base Materials (Ototo)
        mat_amount = data.get("base_materials_amount")
        if mat_amount is not None:
            try:
                amt = int(mat_amount)
                if hasattr(s.ototo, "base_materials") and hasattr(s.ototo.base_materials, "materials"):
                    for mat in s.ototo.base_materials.materials:
                        mat.amount = amt
            except Exception as e:
                print(f"Error setting base materials: {e}")

        # Engineers Max
        if data.get("max_engineers", False):
            try:
                s.ototo.engineers = 5
            except Exception as e:
                print(f"Error setting engineers: {e}")

        # Unlock & Max Cannons
        if data.get("unlock_max_cannons", False):
            try:
                if s.ototo.cannons is None:
                    s.ototo.cannons = core.game.gamoto.ototo.Cannons.init(s.game_version)
                for cannon_id in range(1, 9):
                    cannon = s.ototo.get_cannon(cannon_id)
                    if cannon:
                        cannon.development = 3
                        cannon.levels = [30, 30, 30]
            except Exception as e:
                print(f"Error maxing cannons: {e}")

        # Cat Shrine Max
        if data.get("max_cat_shrine", False):
            try:
                if hasattr(s, "cat_shrine"):
                    s.cat_shrine.level = 30
                    s.cat_shrine.xp = 100000000
            except Exception as e:
                print(f"Error maxing cat shrine: {e}")

        # Special skills max (Cat Cannon Power, Recharge, Castle HP, etc.)
        if data.get("max_special_skills", False):
            try:
                if hasattr(s, "special_skills") and hasattr(s.special_skills, "skills"):
                    for skill in s.special_skills.skills:
                        if hasattr(skill, "max_upgrade_level"):
                            skill.upgrade = skill.max_upgrade_level
            except Exception as e:
                print(f"Error maxing special skills: {e}")

        return self.pack_result(s, is_stateless)

    # ==========================================
    # 7. FIXES & EXTRAS
    # ==========================================
    def edit_fixes_and_extras(self, data: Dict[str, Any]) -> Dict[str, Any]:
        s, is_stateless = self.resolve_save(data)

        # Fix HGT00 Time Errors
        if data.get("fix_time", False):
            now = datetime.datetime.now()
            s.date_3 = now
            s.timestamp = now.timestamp()
            s.energy_penalty_timestamp = now.timestamp()

        # Fix Gamatoto Crash
        if data.get("fix_gamatoto", False):
            s.gamatoto.skin = 2

        # Fix Ototo Crash
        if data.get("fix_ototo", False):
            s.ototo.cannons = core.game.gamoto.ototo.Cannons.init(s.game_version)

        # Fix Officer Pass Crash
        if data.get("fix_officer_pass", False):
            try:
                s.officer_pass.reset(s)
            except Exception:
                pass

        # Unlock all 10 lineup slots
        if data.get("unlock_lineups", False):
            try:
                s.cleared_slots.slots = [True] * 10
            except Exception:
                pass

        # Unlock all medals
        if data.get("unlock_medals", False):
            try:
                medal_names = core.core_data.get_medal_names(s)
                if medal_names and medal_names.medal_names:
                    for i in range(len(medal_names.medal_names)):
                        s.medals.add_medal(i)
            except Exception as e:
                print(f"Error unlocking medals: {e}")

        # Clear missions
        if data.get("clear_missions", False):
            try:
                if hasattr(s, "missions") and hasattr(s.missions, "clear_states"):
                    for m_id in list(s.missions.clear_states.keys()):
                        s.missions.clear_states[m_id] = 4
            except Exception as e:
                print(f"Error clearing missions: {e}")

        # Unlock enemy guide
        if data.get("unlock_enemy_guide", False):
            try:
                s.unlock_enemy_guide = 1
                if hasattr(s, "enemy_guide"):
                    s.enemy_guide = [1] * len(s.enemy_guide)
            except Exception as e:
                print(f"Error unlocking enemy guide: {e}")

        # Gold pass activate
        if data.get("unlock_gold_pass", False):
            try:
                s.officer_pass.officer_pass = 1
            except Exception:
                pass

        # Reset gambling events (Wildcat slots)
        if data.get("reset_gambling", False):
            try:
                core.GamblingEvent.reset_events(s)
            except Exception:
                pass

        # Unban account (Create new inquiry code & server account)
        if data.get("unban_account", False):
            try:
                core.ServerHandler(s).create_new_account()
            except Exception as e:
                print(f"Error unbanning account: {e}")

        # Edit playtime
        if "playtime_hours" in data:
            try:
                hours = float(data["playtime_hours"])
                s.timestamp = hours * 3600
            except Exception:
                pass

        return self.pack_result(s, is_stateless)

    # ==========================================
    # 8. ONE-CLICK GOD MODE / SAFE MAX
    # ==========================================
    def apply_one_click(self, safe_mode: bool = True, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Applies comprehensive edits with one click."""
        payload = data.copy() if data else {}
        catfood = 19999 if safe_mode else 45000
        rare_tickets = 99 if safe_mode else 299
        plat_tickets = 9 if safe_mode else 19
        legend_tickets = 9 if safe_mode else 19

        # Currencies
        payload.update({
            "catfood": catfood,
            "xp": 99999999,
            "leadership": 9999,
            "normal_tickets": 999,
            "rare_tickets": rare_tickets,
            "platinum_tickets": plat_tickets,
            "legend_tickets": legend_tickets,
            "platinum_shards": 99,
            "np": 9999,
            "hundred_million_ticket": 100,
        })
        res = self.edit_currencies(payload)
        payload["save_data"] = res["save_data"]

        # Battle Items
        payload.update({"all_amount": 999, "golden_cpu_count": 99})
        res = self.edit_battle_items(payload)
        payload["save_data"] = res["save_data"]

        # Catfruit, Catseyes, Catamins
        payload["all_amount"] = 128
        res = self.edit_catfruit(payload)
        payload["save_data"] = res["save_data"]

        payload["all_amount"] = 99
        res = self.edit_catseyes(payload)
        payload["save_data"] = res["save_data"]

        payload["all_amount"] = 99
        res = self.edit_catamins(payload)
        payload["save_data"] = res["save_data"]

        # Cats (Unlock all, max level 50+90, true forms, ultra forms, talents, guide)
        payload.update({
            "unlock_all": True,
            "upgrade_level": {"base": 50, "plus": 90},
            "unlock_true_form": True,
            "unlock_fourth_form": True,
            "max_talents": True,
            "unlock_guide": True,
        })
        res = self.edit_cats(payload)
        payload["save_data"] = res["save_data"]

        # Stages (Story clear, 100% gold treasures, timed scores, outbreaks, aku)
        payload.update({
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
        res = self.edit_stages(payload)
        payload["save_data"] = res["save_data"]

        # Base & Gamatoto
        payload.update({
            "max_gamatoto": True,
            "legendary_helpers": True,
            "base_materials_amount": 9999,
            "max_engineers": True,
            "unlock_max_cannons": True,
            "max_cat_shrine": True,
            "max_special_skills": True,
        })
        res = self.edit_gamatoto_and_base(payload)
        payload["save_data"] = res["save_data"]

        # Fixes & Extras
        payload.update({
            "fix_time": True,
            "fix_gamatoto": True,
            "fix_ototo": True,
            "fix_officer_pass": True,
            "unlock_lineups": True,
            "unlock_medals": True,
            "clear_missions": True,
            "unlock_enemy_guide": True,
            "unlock_gold_pass": True,
        })
        return self.edit_fixes_and_extras(payload)


# Global service instance
service = BcsfeService()
