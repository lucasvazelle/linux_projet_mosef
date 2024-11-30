#!/bin/bash
python3 -m streamlit run application/webapp.py --server.port 5004 --server.enableTelemetry false --server.address 0.0.0.0
