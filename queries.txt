// 1. Visualize Document to TextUnit relationships
MATCH (d:Document)-[r:HAS_TEXT_UNIT]->(t:TextUnit)
RETURN d, r, t
LIMIT 50;

// 2. Visualize Entity to TextUnit relationships
MATCH (e:Entity)-[r:MENTIONED_IN]->(t:TextUnit)
RETURN e, r, t
LIMIT 50;

// 3. Visualize Relationships between Entities
MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
RETURN e1, r, e2
LIMIT 50;

// 4. Visualize Community to Relationship connections
MATCH (c:Community)-[r:HAS_RELATIONSHIP]->(rel:Relationship)
RETURN c, r, rel
LIMIT 50;

// 5. Visualize Community Reports and their Communities
MATCH (cr:CommunityReport)-[r:REPORTS_ON]->(c:Community)
RETURN cr, r, c
LIMIT 50;

// 6. Visualize the most connected Entities (Updated)
MATCH (e:Entity)
WITH e, COUNT{(e)-[:RELATES_TO]->(:Entity)} AS degree
ORDER BY degree DESC
LIMIT 10
MATCH (e)-[r:RELATES_TO]->(other:Entity)
RETURN e, r, other;

// 7. Visualize TextUnits and their connections to Entities and Relationships
MATCH (t:TextUnit)-[:HAS_ENTITY]->(e:Entity)
MATCH (t)-[:HAS_RELATIONSHIP]->(r:Relationship)
RETURN t, e, r
LIMIT 50;

// 8. Visualize Documents and their associated Entities (via TextUnits)
MATCH (d:Document)-[:HAS_TEXT_UNIT]->(t:TextUnit)-[:HAS_ENTITY]->(e:Entity)
RETURN d, t, e
LIMIT 50;

// 9. Visualize Communities and their TextUnits
MATCH (c:Community)-[:HAS_TEXT_UNIT]->(t:TextUnit)
RETURN c, t
LIMIT 50;

// 10. Visualize Relationships and their associated TextUnits
MATCH (r:Relationship)-[:MENTIONED_IN]->(t:TextUnit)
RETURN r, t
LIMIT 50;

// 11. Visualize Entities of different types and their relationships
MATCH (e1:Entity)-[r:RELATES_TO]->(e2:Entity)
WHERE e1.type <> e2.type
RETURN e1, r, e2
LIMIT 50;

// 12. Visualize the distribution of Entity types
MATCH (e:Entity)
RETURN e.type AS EntityType, COUNT(e) AS Count
ORDER BY Count DESC;

// 13. Visualize the most frequently occurring relationships
MATCH ()-[r:RELATES_TO]->()
RETURN TYPE(r) AS RelationshipType, COUNT(r) AS Count
ORDER BY Count DESC
LIMIT 10;

// 14. Visualize the path from Document to Entity
MATCH path = (d:Document)-[:HAS_TEXT_UNIT]->(t:TextUnit)-[:HAS_ENTITY]->(e:Entity)
RETURN path
LIMIT 25;