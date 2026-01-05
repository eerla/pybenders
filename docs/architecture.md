# PyBenders Architecture

## High-Level Flow
```mermaid
flowchart TD
    subgraph Generation
        A[Content Registry\n(topics/categories)] --> B[LLM Prompts\nsubject-specific templates]
        B --> C[LLM Response]
        C --> D[Validators\nlength/structure checks]
    end

    subgraph Artifacts
        C -->|raw| M[Metadata JSON\nper question/run]
        D -->|approved| E[Image Renderers\n(per content type)]
        E --> F[Carousel Builder\n(6-slide tech)]
        E --> G[Reel Frames\n(5/6-card themed)]
        F --> H[Images\ncarousel/cover/cta]
        G --> I[Images\nreel frames]
    end

    subgraph Video
        I --> J[Video Stitcher\ntransitions + fades]
        J --> K[Audio Picker\nrandom bg music]
        K --> L[Reel MP4\n1080x1920]
    end

    subgraph Storage
        M --> S1[output_1/<subject>/runs/...metadata.json]
        H --> S2[output_1/<subject>/carousels/]
        I --> S3[output_1/<subject>/images/reel/]
        L --> S4[output_1/<subject>/reels/]
        T[tempfile.tempdir\nsubject-scoped temp/] --> J
        T --> L
    end

    subgraph Upload
        L --> U1[Instagram Reel Upload]
        H --> U2[Instagram Carousel Upload]
        U1 --> U3[uploaded/<subject>/<run_date>/reels/]
        U2 --> U4[uploaded/<subject>/<run_date>/carousels/]
    end

    style T fill:#f8f1d8,stroke:#b59b4c,stroke-width:1px
    style J fill:#e3f2fd,stroke:#64b5f6,stroke-width:1px
    style K fill:#e8f5e9,stroke:#81c784,stroke-width:1px
    style E fill:#f3e5f5,stroke:#ba68c8,stroke-width:1px
    style D fill:#fff3e0,stroke:#ffb74d,stroke-width:1px
    style B fill:#ede7f6,stroke:#9575cd,stroke-width:1px
    style A fill:#fffde7,stroke:#ffd54f,stroke-width:1px
    style U1 stroke:#ef5350
    style U2 stroke:#ef5350
```

## Legend
- Generation: topic selection → subject-specific prompts → LLM response → validation
- Artifacts: metadata + rendered images (carousel or reel frames)
- Video: reel assembly with transitions and random background music
- Storage: organized per subject with scoped temp directories
- Upload: Instagram carousel and reel uploads, organized into uploaded/<subject>/<run_date>/
