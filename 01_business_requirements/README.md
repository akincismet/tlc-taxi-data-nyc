Business Requirements Document
NYC Yellow Taxi Data Analysis and Visualization Project
1. Project Overview
The NYC Yellow Taxi Data Analysis and Visualization Project aims to analyze New York City’s yellow taxi data to derive strategic insights into urban transportation dynamics. By leveraging real-world data provided by the NYC Taxi and Limousine Commission (TLC) in PARQUET format, the project employs modern data engineering processes to transform raw data into meaningful, user-friendly visualizations and reports. This project is designed to provide hands-on experience in building a data platform, performing data engineering tasks, and delivering actionable insights through dashboards.

2. Objectives
Analyze Transportation Patterns: Identify high-demand regions, peak hours, and usage trends for yellow taxis in NYC.
Examine Airport Transfers: Evaluate airport-related trips based on metrics such as fares, passenger counts, and trip durations.
Track Temporal Trends: Analyze daily, weekly, and monthly trends in taxi usage to understand temporal patterns.
Define Key Performance Indicators (KPIs): Calculate and visualize metrics such as average trip duration, distance, and fare.
Build a Modern Data Platform: Implement a fully functional data infrastructure using Kubernetes, Docker, and modern data engineering tools.
Deliver Interactive Visualizations: Create user-friendly dashboards for stakeholders to explore data insights.
3. Stakeholders
Data Users:
Project participants (data engineering trainees).
Potential employers reviewing project outputs as part of participants’ portfolios.
Data Providers:
NYC Taxi and Limousine Commission (TLC), providing public yellow taxi trip data.
Project Team:
Data engineering trainees responsible for developing and delivering the project.
Instructors and mentors guiding the project development.
4. Scope
The project encompasses the following key components:

4.1 Data Infrastructure Setup
Deploy a modern data platform using Kubernetes and Docker Desktop.
Configure and integrate the following components:
PostgreSQL: For relational data storage.
MinIO: For object storage.
Nessie Catalog: For data cataloging.
Trino: For distributed SQL querying.
Superset: For data visualization and dashboard creation.
Apache Spark: For large-scale data processing.
Airflow: For workflow orchestration.
4.2 Data Sources
NYC TLC Yellow Taxi Trip Data:
Format: PARQUET.
Frequency: Daily updates.
Content: Trip details including date, time, pick-up/drop-off locations, fares, distances, and passenger counts.
4.3 Data Processing
Data Ingestion:
Download and ingest daily TLC yellow taxi data into the data platform.
Data Cleaning:
Remove incomplete, erroneous, or inconsistent records.
Standardize data formats for consistency.
Data Enrichment:
Derive new columns such as “day,” “hour,” and “month” from date and time fields.
Map pick-up and drop-off locations to NYC boroughs or zones for geospatial analysis.
Data Organization:
Store data in a Lakehouse architecture with Bronze, Silver, and Gold layers.
Bronze: Raw, unprocessed data.
Silver: Cleaned and standardized data.
Gold: Aggregated and enriched data ready for analytics.
4.4 Analysis and Visualization
Density Analysis: Identify high-traffic zones and peak hours for taxi usage.
Airport Transfer Analysis: Analyze trips to/from airports, focusing on fares, passenger counts, and trip metrics.
Time-Based Trends: Visualize daily, weekly, and monthly trends in taxi usage.
KPIs: Calculate and display metrics such as:
Average trip duration.
Average trip distance.
Average fare amount.
Dashboards: Create interactive dashboards using Superset and Trino, including:
Density heatmaps.
Time-series charts.
Airport transfer summaries.
5. Deliverables
A fully functional data platform deployed on Kubernetes.
A data pipeline that ingests, cleans, enriches, and organizes TLC yellow taxi data.
Interactive dashboards with visualizations for density, trends, airport transfers, and KPIs.
A GitHub repository containing the project codebase, with weekly updates and contributions from participants.
A comprehensive project report summarizing the methodology, findings, and insights.
6. Assumptions
Participants have basic knowledge of data engineering concepts (e.g., from VBO Data Engineering Bootcamp or equivalent).
TLC yellow taxi data is publicly available and accessible during the project duration.
Participants have access to necessary hardware and software (e.g., Docker Desktop, Kubernetes).
7. Constraints
Duration: The project spans 6 weeks, with 3-hour sessions every Saturday (10:00–13:00).
Scope Limitation: The project focuses solely on yellow taxi data and does not include other TLC datasets (e.g., green taxis or for-hire vehicles).
No Theoretical Training: The project is 100% practical, with no dedicated theory sessions.
8. Success Criteria
Successful deployment of the data platform with all components fully operational.
Accurate ingestion, cleaning, and enrichment of TLC yellow taxi data.
Delivery of functional dashboards that effectively communicate insights.
Participant contributions to the GitHub repository, demonstrating active involvement in project development.
Ability of participants to articulate project details and outcomes in job interviews or professional settings.
9. Risks and Mitigation
Risk: Incomplete or inconsistent TLC data.
Mitigation: Implement robust data cleaning processes and validate data quality before processing.
Risk: Technical issues with Kubernetes or platform components.
Mitigation: Provide pre-configured setup guides and troubleshooting support during sessions.
Risk: Participants struggling with advanced concepts.
Mitigation: Offer mentorship and peer collaboration opportunities to support learning.
10. Timeline
Week 1: Project definition, requirements analysis, and infrastructure setup (Docker, Kubernetes).
Week 2: Data platform component installation and configuration (PostgreSQL, MinIO, Trino, etc.).
Week 3: Data ingestion and cleaning pipeline development.
Week 4: Data enrichment and modeling (Bronze, Silver, Gold layers).
Week 5: Analysis and visualization development (Superset dashboards).
Week 6: Finalize dashboards, project review, and documentation.
11. Tools and Technologies
Programming Language: Python.
Data Processing: Apache Spark, Trino.
Workflow Orchestration: Airflow.
Visualization: Superset.
Storage: PostgreSQL, MinIO.
Catalog: Nessie.
Containerization: Docker, Kubernetes.
Version Control: GitHub.
12. Approval
This document outlines the business requirements for the NYC Yellow Taxi Data Analysis and Visualization Project. It serves as the foundation for project development and will be referenced throughout the 6-week training program.