import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app.utils import dedupe_entities
from app.schemas import EntityRow, Evidence

def test_dedupe_entities():
    """
    Basic unit test for dedupe_entities: two identical entities should collapse into one.
    """
    rows = [
        EntityRow(
            entity_name="Test Entity",
            entity_type="startup",
            attributes={"a": 1},
            provenance=[Evidence(source_url="http://example.com", evidence_text="foo")],
        ),
        EntityRow(
            entity_name="test entity",  # same name, different case
            entity_type="startup",
            attributes={"b": 2},
            provenance=[Evidence(source_url="http://example.org", evidence_text="bar")],
        ),
    ]

    deduped = dedupe_entities(rows)

    #Only one entity should remain after deduplication.
    assert len(deduped) == 1
    assert deduped[0].entity_name.lower() == "test entity"