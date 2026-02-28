# 04. Graph RAG Assistant (Network Analysis)

The **Graph RAG Assistant** is designed to surface complex fraud patterns that are often invisible in traditional relational databases, such as "fraud rings" where multiple accounts are linked by shared devices, IP addresses, or sequential transfers.

## 🕸️ 1. Why Graph?

Traditional SQL is excellent for rows and columns, but "traversing" deep relationships (e.g., *Who did User A send money to, who then sent it to User B?*) requires complex and slow JOINs. Graph technology treats these links as first-class citizens, making link analysis nearly instantaneous.

## 🔍 2. Investigative Flow

1. **Ask a Network Question**: 
   - *"Find transaction chains longer than 3 hops."*
   - *"Show users sharing the same hardware ID as known fraudster accounts."*
   - *"Show the network of transfers around transaction ID 12345."*
2. **Cypher Recovery Agent**: 
   - Sentinel uses a specialized agent that understands Neo4j's Cypher query language.
   - If the first attempt fails due to syntax hallucinations, the **Self-Repair Loop** automatically fixes and retries the query up to 3 times behind the scenes.
3. **Interactive Visualization**:
   - High-risk nodes are color-coded (e.g., Fraud is Red).
   - You can drag, zoom, and click nodes to explore the raw data attributes on the fly.

## 🚀 3. Visualization Tools

- **Graph Density**: High-density clusters often indicate organized fraud rings.
- **Path Analysis**: Identify "money mule" accounts that exist only to pass funds between other entities.
- **3D Interaction**: Use your mouse to rotate and explore the network from different analytical perspectives.

> [!IMPORTANT]
> Ensure your data has been "projected" to the graph store in the **Data Hub** before starting a graph investigation.
