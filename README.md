# VISTARA

## AI-Enabled Urban Cadastral Mapping Platform

VISTARA is an AI-enabled web platform designed to automate and assist
urban cadastral mapping using drone imagery, orthorectified imagery,
geospatial datasets and GIS analysis.

## Problem

Urban cadastral mapping currently involves significant manual
digitization, field verification and interpretation of geospatial data.

Dense settlements, irregular parcel geometries, overlapping structures
and complex land-use patterns make accurate cadastral mapping
time-consuming and resource intensive.

## Solution

VISTARA combines:

- Artificial Intelligence
- Computer Vision
- GIS
- Spatial Analysis
- WebGIS
- Geospatial databases

to generate preliminary cadastral maps and identify spatial
inconsistencies requiring review.

## Core Pipeline

Sample Drone / ORI Data
        ↓
AI Feature Extraction
        ↓
GIS Processing
        ↓
Cadastral Layer Generation
        ↓
GIS Analysis & Validation
        ↓
Database
        ↓
WebGIS Dashboard

## Main Modules

- Frontend
- Backend
- AI/ML Engine
- GIS Engine
- GIS Analysis Engine
- Database & Dataset Management

## Repository Structure

```text
frontend/        → Web interface and WebGIS
backend/         → FastAPI backend and APIs
ai/              → AI/ML processing
gis/             → GIS processing engine
gis-analysis/    → Spatial analysis and validation
database/        → Database schema and queries
datasets/        → Sample datasets
docs/            → Project documentation
scripts/         → Utility scripts