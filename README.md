# Learning Data Engineering

<div align="center">

![GitHub](https://img.shields.io/github/license/marlonribunal/learning-data-engineering)
![Grader CI](https://github.com/MarlonRibunal/learning-data-engineering/actions/workflows/grader.yml/badge.svg)
![GitHub last commit](https://img.shields.io/github/last-commit/marlonribunal/learning-data-engineering)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Platform](https://img.shields.io/badge/Platform-Mac%20%7C%20Linux%20%7C%20Windows-green)

**A complete, containerized data engineering learning platform**  
*Master modern data engineering in 6 months • Zero local installations • Production-ready projects*

[**Quick Start**](#one-command-setup) • 
[**Learning Path**](#complete-learning-path) • 
[**Tech Stack**](#tech-stack) • 
[**Contribute**](#join-the-community)

</div>


## Welcome to Your Data Engineering Journey!

**Tired of piecing together scattered tutorials and wrestling with complex local setups?** You've found the solution.

This isn't just another tutorial repository—it's a **complete, production-ready learning environment** that mirrors real-world data engineering workflows. Whether you're transitioning into data engineering, leveling up your skills, or building your portfolio, this platform provides everything you need in one place.


### Why This Platform Exists

Data engineering is one of the fastest-growing fields in tech, but learning it effectively requires:
- **Real infrastructure** (not just isolated code examples)
- **Production patterns** (not just theoretical concepts)  
- **Portfolio projects** (not just hello-world tutorials)
- **Community support** (not just solo learning)

We've built the platform we wish existed when we started our data engineering journeys.


## What Makes This Different?

| Traditional Learning | This Platform |
|---------------------|---------------|
| Scattered tutorials | **Structured 6-month blueprint** |
| Local installations | **100% containerized** |
| Theoretical concepts | **Real portfolio projects** |
| Solo learning | **Community-driven** |
| Hello-world examples | **Production-grade code** |
| Static content | **Active development** |


## One-Command Setup

> **Windows Users:** Use Git Bash • **Mac/Linux Users:** Use Terminal

```bash
git clone https://github.com/marlonribunal/learning-data-engineering.git
cd learning-data-engineering
./bootstrap.sh
```

**That's it!** Your complete data engineering environment automatically builds and will be ready at:

| Service | URL | Credentials |
|---------|-----|-------------|
| **Airflow** | http://localhost:8080 | `admin` / `admin` |
| **Streamlit Dashboard** | http://localhost:8501 | - |
| **PGAdmin** | http://localhost:8081 | `admin@datamart.com` / `admin` |
| **Redpanda Console** | http://localhost:8082 | - |


## Start Here — Learn by Doing (60 seconds)

`./bootstrap.sh` above just starts the raw infrastructure. To actually **learn by
doing** — get real exercises that the platform grades against the live stack — use
the learning platform:

```bash
./platform.sh
```

One command: it creates a Python virtualenv, installs the platform, brings the data
stack up (waits until it's ready), and opens the interactive lesson-runner at
**http://localhost:8501**. Pick a task, write real SQL / dbt / Airflow, and hit
**Check my work** — the grader runs your work against the real Postgres, dbt, and
Airflow, not a simulation. Finish the capstone and it hands you a shareable
**portfolio artifact** to commit to your own GitHub.

Prefer the terminal?

```bash
./platform.sh setup                          # venv + dependencies (one time)
./platform.sh up                             # bring the stack up
./scripts/check.sh status                    # progress dashboard + your next task
./scripts/check.sh start sql-fundamentals select-columns   # scaffold the first task
./scripts/check.sh check sql-fundamentals select-columns   # grade it
./platform.sh down                           # stop the stack when you're done
```

How grading works: the committed file for each task is an incomplete **scaffold** —
you edit it, and the grader checks correctness (not just that it runs). A task is
`pass` only when your work is actually right. A `?? / could not run` result means the
stack is down (start it with `./platform.sh up`), never that your answer was wrong.


## Study in a Single Container (Docker)

Want it *ready whenever you feel like studying*, with zero local setup and your
progress saved between sessions? Build the self-contained study image once and run it:

```bash
docker build -t learn-data-engineering .
docker run -d -p 8501:8501 -v learn-data-engineering-state:/app/state --name learn-data-engineering learn-data-engineering
# open http://localhost:8501
```

One image bundles the learning app, an **embedded Postgres warehouse**, and a
**Java 17 + PySpark** runtime — so the SQL, ingestion, data-quality, serving,
security, architecture, Spark, real-time, and all pure-Python levels grade right
inside the container. No `docker compose`, no venv.

**Your progress persists.** Everything that matters — the levels you've cleared
(`.progress.json`), your submitted code (`submissions/`), and the warehouse data —
lives on the `learn-data-engineering-state` **named volume**. Stop the container, reboot your
laptop, come back next week — the levels you finished stay finished:

```bash
docker stop learn-data-engineering     # done for now — progress is safe on the volume
docker start learn-data-engineering    # pick up exactly where you left off
```

A handful of tool-specific levels (a real dbt build, live Airflow DAGs, the
Redpanda streaming broker) still need the full multi-service stack — use
`./platform.sh up` for those. Everything else works in the single container.

### When you get stuck

Every level ships a built-in **hint ladder**: fail a check and a *Stuck? Show a
hint* button reveals author-written hints one at a time — a nudge, then the
concept, then a near-answer — matched to the exact check you failed. It's fully
offline and your place in the ladder is saved with the rest of your progress.

Want a **personal, code-aware nudge**? Open **Settings** in the sidebar and turn
on the AI tutor. Pick your provider — **Anthropic (Claude)** or **OpenAI (GPT)** —
paste an API key, and an *Ask the tutor* button appears on a failed check. It
sends *your* code and the exact failure to your chosen model and returns one
Socratic hint — **never the answer**.

It's strictly opt-in and private: the tutor is **off until you turn it on**, your
key is stored locally on the state volume (`.tutor.json`, gitignored, owner-only)
and persists across restarts, and nothing leaves the machine except the tutor
requests you trigger. With the tutor off, the offline hint ladders are the whole
story.

Prefer env vars (e.g. for a headless run)? Set `LDE_TUTOR_KEY` — it acts as a
fallback key and enables the tutor automatically:

```bash
docker run -d -p 8501:8501 -v learn-data-engineering-state:/app/state \
  -e LDE_TUTOR_KEY=sk-ant-...    # optional — unlocks the AI tutor
  --name learn-data-engineering learn-data-engineering
```

`LDE_TUTOR_MODEL` overrides the model. In-app Settings always take precedence
over the env vars.


## Complete Learning Path

**Learning cadence: by sprint.** The path runs across **five phases — Foundations → Scaling → Real-time → Production → Capstone**, 20 sprints in all. Each sprint is a focused set of hands-on levels with a clear **Focus** and targeted **Skills**. Browse it live in the app's **Curriculum** page.

### Phase 1 · Foundations
*The bedrock of every pipeline: query data with SQL, land it reliably in the warehouse, model it with dbt, and schedule it with Airflow. Finish here and you can build and run a batch pipeline end to end.*

| Sprint | Focus | Skills |
|--------|-------|--------|
| **1 · SQL Foundations** | Read data confidently with SQL | SELECT & WHERE, JOIN, GROUP BY, HAVING, CASE, window functions |
| **2 · Cloud Data Ingestion** | Land raw source data cleanly and repeatably | INSERT…SELECT, dedupe, idempotent upserts, incremental loads, CDC, quarantine |
| **3 · Modern Transformation** | Turn raw tables into trustworthy dbt models | dbt models, sources & refs, star schema, aggregations, tests |
| **4 · Workflow Orchestration** | Schedule and chain the pipeline | Airflow DAGs, PythonOperator, task dependencies, schedules, retries |

### Phase 2 · Scaling
*Grow past a single machine and a single tool: distributed processing with Spark, the cloud lakehouse and its cost model, hybrid job orchestration, and the data-quality and serving layers that make output trustworthy and usable.*

| Sprint | Focus | Skills |
|--------|-------|--------|
| **5 · Big Data Processing** | Process data that won't fit on one machine | Spark DataFrames, groupBy/agg, joins, windows, partition & cache |
| **6 · Cloud & Lakehouse** | Work the cloud lakehouse and its cost model | scan cost / FinOps, partition pruning, medallion, Delta MERGE, time travel |
| **7 · Hybrid Pipelines** | Drive remote jobs and stitch systems via APIs | job submit/poll, terminal states, timeouts, success gating, failure handling |
| **8 · Data Quality & Testing** | Prove the data is right before it reaches users | data tests, not-null / unique, orphan / FK checks, range checks, valid sets |
| **9 · Serving & BI** | Shape analytics-ready marts and KPIs | serving marts, headline KPIs, running totals, ranking, customer-360 |

### Phase 3 · Real-time
*Leave batch behind. Work with unbounded event streams — producing and consuming, windowed and stateful aggregation, and the live metrics a real-time dashboard renders.*

| Sprint | Focus | Skills |
|--------|-------|--------|
| **10 · Streaming Data** | Move from batch to event streams | Kafka/Redpanda producers & consumers, JSON, offsets, key partitioning, dedupe |
| **11 · Real-time Analytics** | Aggregate unbounded streams with windows & state | tumbling/sliding/session windows, `F.window`, watermarks, Structured Streaming |
| **12 · Unified Dashboards** | Compute the metrics a live dashboard renders | moving averages, pct change, normalization, top-N, threshold bands |

### Phase 4 · Production
*The difference between "it works on my machine" and "it runs the business": security and governance, warehouse architecture, reliability engineering, on-call incident response, debugging, safe migrations, and the advanced algorithms expected of a senior.*

| Sprint | Focus | Skills |
|--------|-------|--------|
| **13 · Data Security** | Lock down who can see and do what | GRANT / REVOKE, column-level grants, PII masking, read-only roles, row-level security |
| **14 · Architecture & Modeling** | Design dimensions, facts, and history | dimension tables, fact grain, SCD Type 2, daily snapshots, surrogate keys |
| **15 · Production Engineering** | Make pipelines reliable and self-healing | retry / backoff, circuit breakers, error rate & SLAs, freshness, idempotent dedupe |
| **16 · On-Call & Incidents** | Respond when the pager goes off | alert triage, root-cause analysis, backfill windows, recovery verification |
| **17 · Debugging Pipelines** | Find and fix real defects in existing code | reading buggy code, dedup logic, rate / percentage math, revenue filters |
| **18 · Schema Migration** | Evolve schemas without losing data | column rename / remap, backfilling defaults, row-count reconciliation |
| **19 · Advanced Challenges** | Tackle the algorithms senior DEs must know | sessionization, cohort retention, topological sort, blast-radius / graphs |

### Phase 5 · Capstone
*Bring it all together in portfolio-grade projects — a full analytics platform, an incident response, and a stateful streaming pipeline — the pieces you'll walk through in interviews.*

| Sprint | Focus | Skills |
|--------|-------|--------|
| **20 · Capstone Projects** | Integrate everything into end-to-end projects | end-to-end analytics, incident response, stateful streaming |

*For detailed daily breakdowns, weekly goals, and specific learning objectives, see the [Complete Learning Blueprint](docs/blueprint.md).*


## Tech Stack

<div align="center">

| Category | Technologies |
|----------|--------------|
| **Orchestration** | Apache Airflow |
| **Processing** | Python, Pandas, PySpark |
| **Transformation** | dbt Core |
| **Warehousing** | BigQuery, PostgreSQL |
| **Streaming** | Redpanda, Spark Streaming |
| **Dashboard** | Streamlit, Plotly |
| **Infrastructure** | Docker, Docker Compose |

</div>

> ** Flexibility Note:** While we use free-tier and open-source tools to make learning accessible, feel free to swap any component with tools of your choice! The architecture is designed to be modular—replace BigQuery with Snowflake, Airflow with Prefect, or Redpanda with Kafka based on your preferences or workplace requirements.

## What's Included

```
learning-data-engineering/
├── 🐳 Complete Containerized Environment
├── 📚 12 Detailed Sprint Guides
├── 🛠️ Production-Ready Projects
├── 📊 Example Data Pipeline (Datamart Intelligence Platform)
├── 📖 Comprehensive Documentation
└── 🎯 Interview Preparation Materials
```

### Featured Project: Datamart Intelligence Platform

A complete data platform for a fictional e-commerce company featuring:

- **Batch Processing**: Daily ETL with data quality checks
- **Real-time Analytics**: Streaming order processing
- **Hybrid Architecture**: Local orchestration + cloud processing
- **Data Governance**: Comprehensive quality monitoring
- **Business Intelligence**: Interactive Streamlit dashboard

## Quick Commands

```bash
# Start all services
./scripts/start.sh

# Stop services
./scripts/stop.sh

# View service logs
./scripts/logs.sh [service-name]

# Complete cleanup (removes all data)
./scripts/destroy.sh

# Access containers
docker-compose exec airflow-webserver bash
docker-compose exec dbt-service dbt run
```

## Join the Community!

### Call for Contributors

**Are you a data engineer, data scientist, or aspiring data professional?**  
We're building the most comprehensive open-source data engineering learning platform, and we need your expertise!

### How You Can Contribute

#### For Senior Data Engineers:
- **Add advanced patterns**: CDC, data mesh, ML pipelines
- **Create real-world case studies**: E-commerce, fintech, healthcare
- **Contribute production-grade code**: Error handling, monitoring, optimization
- **Mentor**: Code reviews, best practices, architecture guidance

#### For Intermediate Practitioners:
- **Expand project examples**: Add new data sources, transformations
- **Create cheat sheets**: Your favorite tools, optimization techniques
- **Write tutorials**: Debugging guides, performance tuning
- **Improve documentation**: Clarify concepts, add examples

#### For Beginners:
- **Test the learning path**: Provide feedback on clarity and progression
- **Report issues**: Found something confusing? Let us know!
- **Suggest improvements**: What would help you learn better?
- **Share your journey**: Blog posts, success stories

### Contribution Areas

| Area | Examples | Skill Level |
|------|----------|-------------|
| **Data Pipelines** | Add CDC, error handling, monitoring | Intermediate+ |
| **dbt Models** | Advanced patterns, custom tests | All Levels |
| **Airflow DAGs** | Complex dependencies, custom operators | Intermediate+ |
| **Streaming** | Kafka connectors, stateful processing | Advanced |
| **Dashboard** | New visualizations, real-time features | All Levels |
| **Documentation** | Guides, tutorials, best practices | All Levels |

### First Time Contributors

**Good first issues:**
- [ ] Add more dbt test examples
- [ ] Create additional Streamlit visualization
- [ ] Write a troubleshooting guide for common setup issues
- [ ] Add more SQL query examples
- [ ] Create a glossary of data engineering terms

### Contribution Process

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Project Roadmap

- [ ] **Phase 1**: Core platform (Complete)
- [ ] **Phase 2**: Advanced patterns (In Progress)
- [ ] **Phase 3**: Real-world case studies (Planned)
- [ ] **Phase 4**: Enterprise features (Future)

## Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Port conflicts** | Check ports 8080, 8501, 8081, 8082 are free |
| **Docker not running** | Start Docker Desktop first |
| **Low memory** | Allocate 4-8GB RAM to Docker |
| **Windows permissions** | Use Git Bash instead of PowerShell |

### Reset Everything

```bash
./scripts/destroy.sh
./bootstrap.sh
```

## Learning Resources

- [**The Data Engineering Lifecycle**](docs/data-engineering-lifecycle.md) - How the platform maps to the framework from *Fundamentals of Data Engineering* (Reis & Housley)
- [**Full Learning Blueprint**](docs/blueprint.md) - Complete 6-month roadmap
- [**Sprint-by-Sprint Guides**](docs/sprint-guides/) - Detailed weekly plans
- [**Tool Cheatsheets**](docs/cheatsheets/) - Quick references
- [**Glossary**](docs/cheatsheets/glossary.md) - Plain-English data engineering terms
- [**Career Guides**](docs/career/) - Interview prep, system design, and turning your passed sprints into a portfolio
- [**Project Documentation**](projects/datamart-intelligence-platform/) - Example implementations

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**, and AGPLv3 is its **sole license** — see the [LICENSE](LICENSE) file for the full text.

If you run a modified version of this software as a network service, AGPLv3 requires you to make your modified source available to its users.

## 🙏 Acknowledgments

- Built with for the data community
- Inspired by modern data stack best practices
- Supported by contributors worldwide

---

<div align="center">

### **Ready to master data engineering?**
**Star this repo if you find it helpful!**

** [Get Started](#one-command-setup) • [Contribute](#join-the-community) • [Learn More](docs/blueprint.md)**

*Join us in building the world's best data engineering learning platform!*

</div>
