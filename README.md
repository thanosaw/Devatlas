
💡 Inspiration

DevAtlas is inspired by the daily struggles of the 3 devs on this project (the product designer is writing this :D). They face the bottleneck of spending over 4 hours per session trying to find which developer is behind the code. Based on our research, they are not alone...

70% of developers say unclear ownership slows down their ability to fix bugs and make updates - GitHub Octoverse Report 2023

Every developer has struggled with finding who owns an unfamiliar piece of code. We were inspired by how much time is wasted during handoffs, onboarding, and bug fixes simply because ownership is unclear. We wanted to create a tool that makes it effortless to answer, "Who built this?" and "Who should I ask?" — especially as teams grow and codebases get more complex.
🦾 What it does

DevAtlas helps developers quickly find the correct developers who worked on a specific part of a project last. By searching questions like "Which dev owns user authentication?", users instantly see a clean ownership profile with the org, team, manager, recent activity, and expertise. It removes the usual friction of hunting through Git histories, Slack messages, or tribal knowledge. We plan to integrate DevAtlas into the work styles of developers, seamlessly solving a major pain point in their daily work life.
⚒️ How we built it

Backend: FastAPI with Python webhook handlers Data Sources: GitHub API, Slack API, Email webhooks Data Processing: Custom Python processors with embedding generation Storage: Neo4j Knowledge Graph Database, JSON intermediate storage Frontend: Next.js and Remix Containerization: Docker AI/ML: Gemini, ASI-1-Mini, custom GraphRAG system,
🏃‍♂️ Challenges we ran into

Our team tackled significant technical hurdles in building a comprehensive knowledge system, particularly in designing an efficient Neo4j schema that could represent complex relationships between diverse entities. We wrestled with integrating heterogeneous data formats from GitHub and Slack while managing API rate limits and ensuring data freshness. Performance optimization proved challenging for large datasets, requiring careful query tuning and implementing effective deduplication strategies to maintain data integrity.
👏🏼 Accomplishments that we're proud of

We successfully built a unified knowledge graph that seamlessly connects GitHub repositories, pull requests, users, and Slack communications within a single cohesive system. Our data integration pipeline efficiently processes information from multiple platforms, enabling real-time synchronization and robust semantic search capabilities. The intelligent RAG system we developed provides context-aware analysis through an intuitive API that utilizes our Knowledge Graph that we built on a Neo4j database via a GraphRAG + Embedding Hybrid approach, delivering meaningful insights that extend beyond what traditional developer tools can offer.
😻 What we learned

We mastered integrating push notifications from Slack and GitHub into our agentic system by developing robust webhook handlers and implementing efficient polling mechanisms that respect API rate limits. Our experience with Neo4j demonstrated how knowledge graphs can effectively model complex relationships between developers, code, and communications. Additionally, we gained valuable insights into building a smart GraphRAG system that leverages our self-collected data to provide contextually relevant answers about development activities across platforms.
🚀 What's next for DevAtlas

    Integration with internal tools like Jira and Linear to track live work and recent changes
    Smart recommendations, like suggesting the best reviewers for pull requests based on ownership and expertise
    Auto-generation of quarterly performance reports and structured evaluations for any employee based on code contributions and chat responses

