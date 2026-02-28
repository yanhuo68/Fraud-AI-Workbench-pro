import pytest
from agents.cypher_recovery_agent import repair_cypher_text, validate_cypher_safety

def test_repair_missing_return():
    cypher = "MATCH (u:Users {name: 'Alice'})"
    repaired = repair_cypher_text(cypher)
    assert "RETURN * LIMIT 50" in repaired
    
    cypher = "MATCH (u:Users) WHERE u.age > 20"
    repaired = repair_cypher_text(cypher)
    assert "RETURN * LIMIT 50" in repaired

def test_repair_swapped_comprehension():
    # Bad syntax: [expr | var IN list]
    cypher = "MATCH (n) RETURN [u.name | u IN labels(n)]"
    repaired = repair_cypher_text(cypher)
    # Correct syntax: [var IN list | expr]
    assert "[u IN labels(n) | u.name]" in repaired

def test_validate_cypher_safety_banned():
    # Test GROUP BY
    err = validate_cypher_safety("MATCH (n) RETURN n.name GROUP BY n.name")
    assert "GROUP BY" in err
    
    # Test Parameters
    err = validate_cypher_safety("MATCH (n {id: $id}) RETURN n")
    assert "parameter" in err
    
    # Test size() on relationships
    err = validate_cypher_safety("MATCH (u:Users) RETURN size((u)-[:LINKED_TO]-())")
    assert "size(" in err
    
    # Test Safe Query
    err = validate_cypher_safety("MATCH (u:Users) RETURN u LIMIT 50")
    assert err is None

def test_repair_trailing_clauses():
    cypher = "MATCH (u:Users) WITH u, count(u) as c"
    repaired = repair_cypher_text(cypher)
    assert "RETURN * LIMIT 50" in repaired
