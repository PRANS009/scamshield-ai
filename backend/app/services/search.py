import asyncio
import copy
import time
from collections import OrderedDict
import httpx
from app import config
from app.security.validation import safe_link, domain, public_term
from app.database.store import now
from app.schemas.core import Source

class SearchError(Exception):
    pass

class SearchService:
    def __init__(self, key=None, transport=None):
        self.key = config.SERPAPI_KEY if key is None else key
        self.transport = transport
        self.cache = OrderedDict()
        self.gate = asyncio.Semaphore(4)

    async def request(self, engine, query):
        if not self.key:
            raise SearchError('SERPAPI_API_KEY is not configured. Live research was not performed.')
        cache_key = (engine, query)
        cached = self.cache.get(cache_key)
        if cached and time.monotonic() - cached[0] < 600:
            return copy.deepcopy(cached[1])
        async with self.gate:
            async with httpx.AsyncClient(timeout=12, transport=self.transport, follow_redirects=False) as client:
                for attempt in range(2):
                    try:
                        response = await client.get('https://serpapi.com/search.json',params={
                            'engine':engine,'q':query,'api_key':self.key,'hl':'en','gl':'in'})
                        if response.status_code == 429:
                            raise SearchError('SerpApi rate limit or credit limit reached. Please retry later.')
                        if response.status_code in (500,502,503,504) and attempt == 0:
                            await asyncio.sleep(.25)
                            continue
                        response.raise_for_status()
                        result = response.json()
                        if result.get('error'):
                            raise SearchError('SerpApi returned an error; check your account credits and search settings.')
                        result['_retrieved_at'] = now()
                        self.cache[cache_key] = (time.monotonic(),copy.deepcopy(result))
                        while len(self.cache)>128:
                            self.cache.popitem(last=False)
                        return result
                    except httpx.TimeoutException:
                        if attempt == 0:
                            continue
                        raise SearchError('SerpApi timed out. Research is incomplete.') from None
                    except (httpx.HTTPError,ValueError):
                        raise SearchError('SerpApi request failed. No live results are available for this query.') from None

    async def web(self, query, claimed_domain=''):
        result = await self.request('google',query)
        items = []
        for item in result.get('organic_results',[])[:8]:
            url = safe_link(item.get('link',''))
            if not url:
                continue
            host = domain(url)
            classification = 'Third-party search result'
            if claimed_domain and (host == claimed_domain or host.endswith('.'+claimed_domain)):
                classification = 'Matches user-supplied official domain (ownership unverified)'
            elif host.endswith(('.gov.in','.nic.in')):
                classification = 'Government domain; relevance requires review'
            items.append(Source(id='',title=str(item.get('title','Untitled'))[:300],url=url,
                snippet=str(item.get('snippet',''))[:1500],query=query,retrieved_at=result['_retrieved_at'],source_type=classification))
        return items

    async def jobs(self, role, location, skills='', preference='', salary=''):
        query = ' '.join(public_term(x) for x in [role,'jobs',location,skills,preference,salary] if x).strip()
        result = await self.request('google_jobs',query)
        jobs=[]
        for item in result.get('jobs_results',[])[:10]:
            links = []
            for link in item.get('apply_options',[]):
                safe = safe_link(link.get('link',''))
                if safe:
                    links.append({'title':str(link.get('title','Source'))[:100],'url':safe})
            for link in item.get('related_links',[]):
                safe = safe_link(link.get('link',''))
                if safe and safe not in [x['url'] for x in links]:
                    links.append({'title':str(link.get('text','Source'))[:100],'url':safe})
            jobs.append({'id':item.get('job_id',''),'title':item.get('title',''),'company':item.get('company_name',''),
                'location':item.get('location',''),'description':str(item.get('description',''))[:12000],
                'via':item.get('via',''),'posted_at':item.get('detected_extensions',{}).get('posted_at','Unknown'),
                'salary':item.get('detected_extensions',{}).get('salary','Not disclosed'),'links':links,
                'retrieved_at':result['_retrieved_at'],'verification':'Unverified public listing'})
        return {'query':query,'jobs':jobs,'sample_count':len(jobs),'retrieved_at':result['_retrieved_at'],
            'notice':'Search sample only. Listings, dates and salary claims are not independently verified; salary filters are search terms, not guaranteed constraints.'}

search_service = SearchService()
