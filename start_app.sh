#!/bin/bash
pip3 install -r requirements.txt
python3 -m streamlit run application/webapp.py --server.port 5004 
