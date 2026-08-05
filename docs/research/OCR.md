                Document
                    │
                    ▼
        Detect document characteristics   -> 
                    │
        ┌───────────┴───────────┐
        │                       │
Has embedded text?      Scanned / Images only?
        │                       │
      Yes                      Yes
        │                       │
        ▼                       ▼
     Docling             OCR (Arabic/English)
                                │
                                ▼
                             Docling
                                │
                                ▼
                   Structured Document
                                │
                                ▼
              Chunking + Metadata Extraction
                                │
                                ▼
                 Knowledge Graph + Embeddings
                                │
                                ▼
                             Vector DB
                             
                             
                             
                             
                             
                             
                             
                             
                             
                             
                             
                             
                             
                             split 
                             page 
                             Analyser 
        preprocessing : Has selectable text, Estimated text coverage, Image coverage, Language, Rotation, Scan quality            
