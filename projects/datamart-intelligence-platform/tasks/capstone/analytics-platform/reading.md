## The whole lifecycle, in one pipeline

This capstone is where the pieces become an architecture. Raw orders → a tested dbt
mart → orchestrated by Airflow → verified end-to-end: that's the **data engineering
lifecycle** (Reis & Housley) running as one system —
Generation → Ingestion → Storage → Transformation → Serving, with the undercurrents
(quality, orchestration) woven through.

What makes it a *platform* rather than a script:

- **Composition.** No single tool does it all — dbt transforms and tests, Airflow
  orchestrates and retries, the warehouse stores and serves. Data engineering is
  largely the art of wiring specialized tools into a coherent whole.
- **Verification end-to-end.** The capstone grades the *chain* — the model builds
  *and* passes its tests *and* the DAG runs green — because in production, a pipeline
  is only as trustworthy as its weakest link. Each stage tested in isolation isn't
  enough; the integration is where real bugs hide.
- **A portfolio artifact.** It emits proof you can show — because the ability to
  *demonstrate* a working, tested, end-to-end pipeline is what actually lands data
  jobs. "I built and verified this" beats "I know dbt."

Stepping back: everything upstream in the course — SQL, modeling, quality,
orchestration — existed to make a moment like this possible. A reliable pipeline
from raw data to a trusted number is the entire job, distilled.

*Go deeper: the data engineering lifecycle (Reis & Housley); pipeline integration
testing; building a DE portfolio.*
