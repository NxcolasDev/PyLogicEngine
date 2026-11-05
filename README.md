<div align="center">
  <img src="assets/logo.png" alt="PyLogic Logo" width="180"/>
  <h1>PyLogic Engine & Cloud Analytics</h1>
  <p><b>CLI purista em Python para análise de algoritmo com telemetria assíncrona Serverless (AWS SQS/Lambda)</b></p>

  [![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
  [![AWS SQS](https://img.shields.io/badge/AWS_SQS-Event--Driven-FF9900?style=for-the-badge&logo=amazonaws&logoColor=white)](https://aws.amazon.com/)
  [![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
  [![Clean Architecture](https://img.shields.io/badge/Architecture-Clean-green?style=for-the-badge)](#arquitetura)
</div>

---

## 📌 Visão Geral

O **PyLogic Engine** é um ambiente interativo via terminal voltado ao treino de lógica de programação e algoritmos de alta performance sem dependências externas. O motor possui integração nativa e desacoplada com pipelines de telemetria serverless via AWS SQS.

## 🏗️ Arquitetura do Sistema

```text
[ User Interactive CLI ]
         │
         ▼
[ Domain Analytics Engine ] (Pure Python Standard Library)
         │
         ▼ (Async Telemetry)
[ AWS SQS / Event Queue ]
         │
         ▼
[ AWS Lambda Container / Analytics Processing ]