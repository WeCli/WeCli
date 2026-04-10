import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import services.team_preset_assets as team_preset_assets


class TeamPresetAssetsTests(unittest.TestCase):
    def test_repo_ships_expected_presets(self):
        presets = team_preset_assets.list_team_presets()
        preset_ids = {item["preset_id"] for item in presets}
        self.assertEqual(len(presets), 14)
        self.assertTrue({"ming-neige", "tang-sansheng-beta", "modern-ceo", "hanlin-novel-studio"}.issubset(preset_ids))
        self.assertTrue({"code-team", "social-account-control"}.issubset(preset_ids))

    def test_list_and_install_team_preset(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            preset_root = root / "assets"
            preset_dir = preset_root / "modern-ceo"
            workflow_dir = preset_dir / "oasis" / "yaml"
            workflow_dir.mkdir(parents=True, exist_ok=True)
            (preset_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "preset_id": "modern-ceo",
                        "name": "现代企业制",
                        "default_team_name": "现代企业制",
                        "role_count": 2,
                        "workflow_files": ["modern.yaml"],
                        "tags": ["enterprise"],
                    },
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (preset_dir / "internal_agents.json").write_text(
                json.dumps(
                    [
                        {"name": "CEO", "tag": "ceo"},
                        {"name": "CTO", "tag": "cto"},
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (preset_dir / "oasis_experts.json").write_text(
                json.dumps(
                    [
                        {"name": "CEO", "tag": "ceo", "persona": "lead", "temperature": 0.4},
                        {"name": "CTO", "tag": "cto", "persona": "ship", "temperature": 0.4},
                    ],
                    ensure_ascii=False,
                    indent=2,
                ),
                encoding="utf-8",
            )
            (preset_dir / "source_map.json").write_text(
                json.dumps({"source": "test"}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            (workflow_dir / "modern.yaml").write_text("version: 2\nrepeat: false\nplan: []\nedges: []\n", encoding="utf-8")

            original_preset_root = team_preset_assets.PRESET_ROOT
            team_preset_assets.PRESET_ROOT = preset_root
            try:
                listed = team_preset_assets.list_team_presets()
                self.assertEqual(len(listed), 1)
                self.assertEqual(listed[0]["preset_id"], "modern-ceo")

                result = team_preset_assets.install_team_preset(
                    user_id="alice",
                    team_name="Modern Ops",
                    preset_id="modern-ceo",
                    project_root=root,
                )
                self.assertEqual(result["team"], "Modern Ops")
                self.assertEqual(result["internal_agents"], 2)
                self.assertEqual(result["workflow_files"], ["modern.yaml"])

                team_dir = root / "data" / "user_files" / "alice" / "teams" / "Modern Ops"
                installed_agents = json.loads((team_dir / "internal_agents.json").read_text(encoding="utf-8"))
                self.assertEqual(len(installed_agents), 2)
                self.assertTrue(all(item.get("session") for item in installed_agents))
                self.assertTrue((team_dir / "wecli_preset_manifest.json").exists())
                self.assertTrue((team_dir / "oasis" / "yaml" / "modern.yaml").exists())
            finally:
                team_preset_assets.PRESET_ROOT = original_preset_root

    def test_new_presets_install_with_project_scale_workflows(self):
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            for preset_id, team_name, min_roles in [
                ("code-team", "Code Team Demo", 6),
                ("social-account-control", "Social Control Demo", 7),
            ]:
                bundle = team_preset_assets.get_team_preset_bundle(preset_id)
                self.assertIsNotNone(bundle)
                manifest = bundle["manifest"]
                self.assertEqual(manifest["role_count"], min_roles)
                self.assertGreaterEqual(len(bundle["workflows"]), 1)

                role_tags = {item["tag"] for item in bundle["internal_agents"]}
                self.assertEqual(len(role_tags), min_roles)

                install_result = team_preset_assets.install_team_preset(
                    user_id="alice",
                    team_name=team_name,
                    preset_id=preset_id,
                    project_root=root,
                )
                self.assertEqual(install_result["internal_agents"], min_roles)
                self.assertEqual(install_result["experts"], min_roles)

                installed_team_dir = root / "data" / "user_files" / "alice" / "teams" / team_name
                self.assertTrue((installed_team_dir / "wecli_preset_manifest.json").exists())
                self.assertTrue((installed_team_dir / "wecli_preset_source_map.json").exists())

                for workflow_file in install_result["workflow_files"]:
                    workflow_path = installed_team_dir / "oasis" / "yaml" / workflow_file
                    self.assertTrue(workflow_path.exists())
                    workflow = yaml.safe_load(workflow_path.read_text(encoding="utf-8"))
                    plan = workflow["plan"]
                    edges = workflow["edges"]
                    self.assertTrue(any("manual" in step and step["manual"]["author"] == "begin" for step in plan))
                    self.assertTrue(any("manual" in step and step["manual"]["author"] == "bend" for step in plan))
                    expert_tags = {
                        step["expert"].split("#", 1)[0]
                        for step in plan
                        if isinstance(step, dict) and "expert" in step
                    }
                    self.assertGreaterEqual(len(expert_tags), min_roles - 1)
                    self.assertTrue(expert_tags.issubset(role_tags))
                    self.assertGreaterEqual(len(edges), min_roles)
