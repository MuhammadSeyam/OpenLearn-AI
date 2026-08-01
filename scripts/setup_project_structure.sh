#!/usr/bin/env bash

set -e

echo "🚀 Creating OpenLearn AI project structure..."

###############################################################################
# Root folders
###############################################################################

mkdir -p \
docs \
backend \
frontend \
scripts \
.github \
assets \
datasets \
experiments \
infrastructure \
models \
planning \
presentations \
services

###############################################################################
# Documentation
###############################################################################

mkdir -p \
docs/project \
docs/architecture \
docs/architecture/ADR \
docs/research \
docs/api \
docs/meeting-notes

###############################################################################
# Backend
###############################################################################

mkdir -p \
backend/app \
backend/tests \
backend/migrations \
backend/requirements

###############################################################################
# Frontend
###############################################################################

mkdir -p \
frontend/app \
frontend/components \
frontend/features \
frontend/hooks \
frontend/public

###############################################################################
# Models
###############################################################################

mkdir -p \
models/local \
models/prompts \
models/embeddings \
models/configs

###############################################################################
# Services
###############################################################################

mkdir -p \
services/ingestion \
services/ocr \
services/rag \
services/embeddings \
services/knowledge-graph \
services/student-model \
services/adaptive-engine \
services/analytics \
services/generation

###############################################################################
# Infrastructure
###############################################################################

mkdir -p \
infrastructure/docker \
infrastructure/nginx \
infrastructure/monitoring \
infrastructure/kubernetes \
infrastructure/scripts

###############################################################################
# Datasets
###############################################################################

mkdir -p \
datasets/samples \
datasets/benchmarks \
datasets/evaluation

###############################################################################
# Experiments
###############################################################################

mkdir -p \
experiments/notebooks \
experiments/benchmarks \
experiments/prototypes

###############################################################################
# Assets
###############################################################################

mkdir -p \
assets/logo \
assets/diagrams \
assets/screenshots

###############################################################################
# Planning
###############################################################################

mkdir -p \
planning/tasks \
planning/meeting-minutes \
planning/team-roles \
planning/weekly-reports

###############################################################################
# Presentations
###############################################################################

mkdir -p \
presentations/proposal \
presentations/midterm \
presentations/final \
presentations/poster \
presentations/demo

###############################################################################
# GitHub
###############################################################################

mkdir -p \
.github/workflows \
.github/ISSUE_TEMPLATE

###############################################################################
# Create placeholder markdown files
###############################################################################

touch \
CHANGELOG.md \
ROADMAP.md \
CONTRIBUTING.md \
CODE_OF_CONDUCT.md

touch \
docs/project/Project_Report_v4.md \
docs/project/Vision.md \
docs/project/Scope.md \
docs/project/Roadmap.md

touch \
docs/architecture/SystemArchitecture.md \
docs/architecture/HybridArchitecture.md \
docs/architecture/OfflineMode.md \
docs/architecture/CloudMode.md \
docs/architecture/DataFlow.md

touch \
docs/research/LiteratureReview.md \
docs/research/CompetitorAnalysis.md \
docs/research/ModelEvaluation.md \
docs/research/OCR.md \
docs/research/RAG.md \
docs/research/StudentModel.md \
docs/research/AdaptiveLearning.md

touch \
planning/Sprint-01.md \
planning/Sprint-02.md

echo ""
echo "✅ Project structure created successfully!"
