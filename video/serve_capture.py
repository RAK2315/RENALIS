"""Run the real API against an isolated synthetic-demo database for filming."""
import sys
from pathlib import Path
import uvicorn
from backend import app as service

service.DB_PATH=Path(sys.argv[1]).resolve()
service.DB_PATH.parent.mkdir(parents=True,exist_ok=True)
uvicorn.run(service.app,host='127.0.0.1',port=int(sys.argv[2]),log_level='warning')
