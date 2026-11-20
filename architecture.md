flowchart TD

&#x20;   A\[User Interface] --> B\[FastAPI Backend]



&#x20;   B --> C\[Document Upload API]

&#x20;   C --> D\[PDF DOCX Parser]

&#x20;   D --> E\[Text Chunking]

&#x20;   E --> F\[Embedding Generation]

&#x20;   F --> G\[ChromaDB Vector Store]



&#x20;   B --> H\[Chat API]

&#x20;   H --> G

&#x20;   H --> I\[CRM Tool]

&#x20;   I --> J\[CRM REST API]



&#x20;   H --> K\[Order Tools]

&#x20;   K --> L\[PostgreSQL]



&#x20;   H --> M\[LLM]

&#x20;   M --> B

&#x20;   B --> A

