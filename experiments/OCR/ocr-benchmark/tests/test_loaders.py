"""Loader contract tests against the real datasets (read-only).

Misraj materializes its regenerable page cache on first run; later runs reuse
it. These tests are the Phase 0 count gates: 400 / 199 / 85.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

import pytest

from ocrbench.datasets import load_bce, load_custom, load_misraj
from ocrbench.datasets.bce import BCE_ROOT
from ocrbench.datasets.custom import CUSTOM_ROOT
from ocrbench.datasets.misraj import PAGE_CACHE_DIR


@pytest.fixture(scope="module")
def misraj() -> list:
    return load_misraj()


@pytest.fixture(scope="module")
def bce() -> list:
    return load_bce()


@pytest.fixture(scope="module")
def custom() -> list:
    return load_custom()


class TestMisraj:
    def test_count_and_unique_ids(self, misraj):
        assert len(misraj) == 400
        assert len({s.sample_id for s in misraj}) == 400

    def test_non_empty_references(self, misraj):
        assert all(s.reference_text and s.reference_text.strip() for s in misraj)

    def test_materialized_images_exist_in_cache(self, misraj):
        for s in misraj:
            assert s.image_path.is_file()
            assert s.image_path.parent == PAGE_CACHE_DIR
            assert s.image_path.stem == s.sample_id

    def test_no_categories_invented(self, misraj):
        assert all(s.categories == [] for s in misraj)


class TestBCE:
    def test_count_and_unique_ids(self, bce):
        assert len(bce) == 199
        assert len({s.sample_id for s in bce}) == 199

    def test_all_mappings_resolve(self, bce):
        assert all(s.image_path.is_file() for s in bce)
        assert all(s.gt_xml_path is not None and s.gt_xml_path.is_file() for s in bce)

    def test_pairing_is_manifest_driven(self, bce):
        """Filename matching would break the 80 normalized-stem samples."""
        manifest = json.loads((BCE_ROOT / "manifest.json").read_text(encoding="utf-8"))
        by_id = {d["sample_id"]: d for d in manifest["documents"]}
        methods = {s.metadata["mapping_method"] for s in bce}
        assert methods == {"exact", "normalized-stem"}
        assert sum(1 for s in bce if s.metadata["mapping_method"] == "normalized-stem") == 80

        mismatches = 0
        for s in bce:
            if by_id[s.sample_id]["mapping_method"] != "normalized-stem":
                continue
            root = ET.parse(s.gt_xml_path).getroot()
            declared = None
            for el in root.iter():
                if el.tag.endswith("Page"):
                    declared = el.get("imageFilename")
                    break
            if declared is not None and declared != s.image_path.name:
                mismatches += 1
        assert mismatches > 0, (
            "expected XML-declared imageFilenames that differ from shipped "
            "image names — filename pairing would silently corrupt these"
        )

    def test_reading_order_split_198_1(self, bce):
        ro = [s.metadata["reading_order_exists"] for s in bce]
        assert ro.count(True) == 198
        assert ro.count(False) == 1
        without_ro = [s.sample_id for s in bce if not s.metadata["reading_order_exists"]]
        assert without_ro == ["charts__text1-140"]

    def test_categories_from_manifest(self, bce):
        assert {s.categories[0] for s in bce} == {
            "Charts", "Headers", "graphics", "multi-columns",
            "tables", "text and images", "textonly", "titles",
        }


class TestCustom:
    def test_count_and_unique_ids(self, custom):
        assert len(custom) == 85
        assert len({s.sample_id for s in custom}) == 85

    def test_all_gt_mappings_resolve_and_non_empty(self, custom):
        for s in custom:
            assert s.reference_text is not None
            assert s.reference_text.strip()
        assert all(s.image_path.is_file() for s in custom)

    def test_source_types_match_manifest_counts(self, custom):
        pdfs = [s for s in custom if s.metadata["source_type"] == "pdf"]
        images = [s for s in custom if s.metadata["source_type"] == "image"]
        assert len(pdfs) == 58
        assert len(images) == 27
        assert all(s.image_path.suffix == ".pdf" for s in pdfs)
        assert all(s.image_path.suffix in (".png", ".jpg") for s in images)
        assert all(s.image_path.is_relative_to(CUSTOM_ROOT) for s in custom)

    def test_document_level_exception_preserved(self, custom):
        doc_level_pdfs = [
            s for s in custom
            if s.metadata["source_type"] == "pdf" and s.metadata["page"] is None
        ]
        assert len(doc_level_pdfs) == 1
        assert doc_level_pdfs[0].sample_id == "custom_multi_column_004"
        # the 27 standalone images also legitimately carry page=None
        assert sum(1 for s in custom if s.metadata["page"] is None) == 28

    def test_gt_identity_chain(self, custom):
        from ocrbench.datasets.custom import GT_ROOT

        stems = {p.stem for p in GT_ROOT.glob("*.txt")}
        assert stems == {s.sample_id for s in custom}


class TestFailLoudly:
    """Broken inputs must raise, never skip silently."""

    def _write_manifest(self, tmp_root, documents, **extra):
        payload = {
            "schema_version": 4,
            "dataset": "custom",
            "physical_files": len(documents),
            "logical_samples": len(documents),
            "documents": documents,
            **extra,
        }
        tmp_root.mkdir(parents=True, exist_ok=True)
        (tmp_root / "manifest.json").write_text(json.dumps(payload), encoding="utf-8")

    def test_duplicate_sample_id_rejected(self, tmp_path, monkeypatch):
        doc = {
            "sample_id": "dup", "path": "x.pdf", "source_type": "pdf",
            "page": 1, "language": ["en"], "categories": ["c"], "features": {},
        }
        root = tmp_path / "custom"
        self._write_manifest(root, [doc, dict(doc)])
        (root / "x.pdf").write_bytes(b"%PDF-fake")
        gt = tmp_path / "ground_truth"
        gt.mkdir()
        (gt / "dup.txt").write_text("hello", encoding="utf-8")
        monkeypatch.setattr("ocrbench.datasets.custom.CUSTOM_ROOT", root)
        monkeypatch.setattr("ocrbench.datasets.custom.GT_ROOT", gt)
        with pytest.raises(ValueError, match="duplicate sample id"):
            load_custom()

    def test_missing_gt_rejected(self, tmp_path, monkeypatch):
        doc = {
            "sample_id": "nogt", "path": "x.pdf", "source_type": "pdf",
            "page": 1, "language": ["en"], "categories": ["c"], "features": {},
        }
        self._write_manifest(tmp_path / "custom", [doc])
        monkeypatch.setattr("ocrbench.datasets.custom.CUSTOM_ROOT", tmp_path / "custom")
        with pytest.raises(ValueError, match="missing ground truth"):
            load_custom()

    def test_wrong_count_rejected(self, tmp_path, monkeypatch):
        doc = {
            "sample_id": "s1", "path": "x.png", "source_type": "image",
            "page": None, "language": ["en"], "categories": ["c"], "features": {},
        }
        root = tmp_path / "custom"
        self._write_manifest(root, [doc])
        (root / "x.png").write_bytes(b"fake")
        gt = tmp_path / "ground_truth"
        gt.mkdir()
        (gt / "s1.txt").write_text("hello", encoding="utf-8")
        monkeypatch.setattr("ocrbench.datasets.custom.CUSTOM_ROOT", root)
        monkeypatch.setattr("ocrbench.datasets.custom.GT_ROOT", gt)
        with pytest.raises(ValueError, match="expected 85"):
            load_custom()

    def test_unknown_source_type_rejected(self, tmp_path, monkeypatch):
        doc = {
            "sample_id": "s1", "path": "x.docx", "source_type": "word",
            "page": 1, "language": ["en"], "categories": ["c"], "features": {},
        }
        root = tmp_path / "custom"
        self._write_manifest(root, [doc])
        (root / "x.docx").write_bytes(b"fake")
        gt = tmp_path / "ground_truth"
        gt.mkdir()
        (gt / "s1.txt").write_text("hello", encoding="utf-8")
        monkeypatch.setattr("ocrbench.datasets.custom.CUSTOM_ROOT", root)
        monkeypatch.setattr("ocrbench.datasets.custom.GT_ROOT", gt)
        with pytest.raises(ValueError, match="unknown source_type"):
            load_custom()
