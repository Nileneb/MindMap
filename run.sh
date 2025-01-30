#!/bin/sh
python init_db.py
exec "$@"


streamlit run main.py --server.port 7742

#sudo systemctl start postgresql
sudo systemctl enable postgresql