import os,tempfile
os.environ['DATABASE_URL']='sqlite:///'+tempfile.mktemp(prefix='scamshield-tests-',suffix='.db')
os.environ['SERPAPI_API_KEY']=''
os.environ['LLM_API_KEY']=''
import pytest
from fastapi.testclient import TestClient
from app.main import app,visits
from app.database.store import Base,engine
@pytest.fixture
def client():
    Base.metadata.drop_all(engine);visits.clear()
    with TestClient(app) as c:yield c
