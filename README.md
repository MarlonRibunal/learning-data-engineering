# 🚀 Learning Data Engineering

<div align="center">

![GitHub](https://img.shields.io/github/license/marlonribunal/learning-data-engineering)
![GitHub last commit](https://img.shields.io/github/last-commit/marlonribunal/learning-data-engineering)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)
![Platform](https://img.shields.io/badge/Platform-Mac%20%7C%20Linux%20%7C%20Windows-green)

**A complete, containerized data engineering learning platform**  
*Master modern data engineering in 6 months • Zero local installations • Production-ready projects*

[**Quick Start**](#-one-command-setup) • 
[**Learning Path**](#-learning-path) • 
[**Tech Stack**](#-tech-stack) • 
[**Contribute**](#-join-the-community)

</div>

## 🎯 What Makes This Different?

| Traditional Learning | This Platform |
|---------------------|---------------|
| ❌ Scattered tutorials | ✅ **Structured 6-month blueprint** |
| ❌ Local installations | ✅ **100% containerized** |
| ❌ Theoretical concepts | ✅ **Real portfolio projects** |
| ❌ Solo learning | ✅ **Community-driven** |

## 🚀 One-Command Setup

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

## 📚 Complete Learning Path

### 🎓 Phase 1: Foundations (Months 1-2)
**Project: E-Commerce Data Pipeline**

| Sprint | Focus | Skills |
|--------|-------|--------|
| **1** | Cloud Data Ingestion | BigQuery, Python, Data Validation |
| **2** | Modern Transformation | dbt Core, Star Schema, Data Modeling |
| **3** | Workflow Orchestration | Airflow, DAGs, Task Dependencies |

### ⚡ Phase 2: Scaling (Months 3-4)  
**Project: Hybrid Cloud Platform**

| Sprint | Focus | Skills |
|--------|-------|--------|
| **4** | Big Data Processing | Spark, Databricks, Distributed Computing |
| **5** | Hybrid Pipelines | Cloud Integration, API Orchestration |
| **6** | Data Quality | Testing Frameworks, Monitoring, Alerting |

### 🔥 Phase 3: Real-time (Months 5-6)
**Project: Real-time Intelligence Platform**

| Sprint | Focus | Skills |
|--------|-------|--------|
| **7** | Streaming Data | Kafka/Redpanda, Event Processing |
| **8** | Real-time Analytics | Spark Streaming, Stateful Processing |
| **9** | Unified Dashboards | Streamlit, Real-time Visualization |
| **10-12** | Portfolio & Career | Interviews, System Design, Job Search |

## 🛠️ Tech Stack

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

## 📁 What's Included

```
learning-data-engineering/
├── 🐳 Complete Containerized Environment
├── 📚 12 Detailed Sprint Guides
├── 🛠️ Production-Ready Projects
├── 📊 Example Data Pipeline (Datamart Intelligence Platform)
├── 📖 Comprehensive Documentation
└── 🎯 Interview Preparation Materials
```

### 🎯 Featured Project: Datamart Intelligence Platform

A complete data platform for a fictional e-commerce company featuring:

- **Batch Processing**: Daily ETL with data quality checks
- **Real-time Analytics**: Streaming order processing
- **Hybrid Architecture**: Local orchestration + cloud processing
- **Data Governance**: Comprehensive quality monitoring
- **Business Intelligence**: Interactive Streamlit dashboard

## 🚀 Quick Commands

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

## 👥 Join the Community!

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

## 🆘 Troubleshooting

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

## 📖 Learning Resources

- [**Full Learning Blueprint**](docs/blueprint.md) - Complete 6-month roadmap
- [**Sprint-by-Sprint Guides**](docs/sprint-guides/) - Detailed weekly plans
- [**Tool Cheatsheets**](docs/cheatsheets/) - Quick references
- [**Project Documentation**](projects/datamart-intelligence-platform/) - Example implementations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with for the data community
- Inspired by modern data stack best practices
- Supported by contributors worldwide

---

<div align="center">

### **Ready to master data engineering?**
**Star this repo if you find it helpful!**

**👉 [Get Started](#-one-command-setup) • [Contribute](#-join-the-community) • [Learn More](docs/blueprint.md)**

*Join us in building the world's best data engineering learning platform!*

</div> ```