import re
from collections import Counter

SKILLS=['python','javascript','typescript','java','c++','c#','react','node.js','express','html','css','sql','postgresql','mongodb','git','docker','kubernetes','aws','azure','linux','fastapi','flask','django','pandas','numpy','pytorch','tensorflow','scikit-learn','machine learning','deep learning','data analysis','excel','power bi','tableau','communication','problem solving','rest api','testing']
ROLE_SKILLS={
    'frontend':['html','css','javascript','typescript','react','git','testing'],
    'backend':['python','sql','fastapi','rest api','git','docker','testing'],
    'data':['python','sql','pandas','numpy','data analysis','excel'],
    'machine learning':['python','pandas','numpy','scikit-learn','machine learning','testing'],
    'full stack':['html','css','javascript','react','node.js','sql','git','testing'],
}

def skills_in(text):
    return sorted(s for s in SKILLS if re.search(r'(?<![\w+#])'+re.escape(s)+r'(?![\w+#])',text,re.I))

def match(resume,description):
    required=skills_in(description); possessed=skills_in(resume)
    matched=sorted(set(required)&set(possessed));missing=sorted(set(required)-set(possessed))
    return {'score':round(100*len(matched)/len(required)) if required else None,'matched':matched,'missing':missing,
        'required':required,'detected_resume_skills':possessed,'requirements':[{'requirement':x,'status':'Matched' if x in matched else 'Unknown',
            'reason':'Keyword present' if x in matched else 'Not found in supplied text; absence is not proof of missing ability'} for x in required],
        'notice':'Transparent keyword relevance against a fixed skill dictionary, not an employer ATS result or a hiring prediction. Education, experience and location requirements need manual review.',
        'suggestions':[f'If you have {x} experience, add a truthful project example showing how you used it.' for x in missing[:8]]}

def roadmap(skills,role,description=''):
    role_key=next((x for x in ROLE_SKILLS if x in role.lower()),'backend' if 'python' in role.lower() else None)
    target=skills_in(description) if description else ROLE_SKILLS.get(role_key,[])
    present=skills_in(skills);missing=[s for s in target if s not in present]
    stages=[]
    for days,focus,selected in [('1–30','Foundations',missing[:3]),('31–60','Build and explain',missing[3:6]),('61–90','Practice and apply',missing[6:])]:
        stages.append({'days':days,'focus':focus,'skills':selected,'task':
            'Build a small project, document your choices, and demonstrate the skills listed here.' if focus!='Practice and apply' else 'Improve your project, practise interview explanations, and apply through verified channels.'})
    questions=[f'Explain how you used {s} in a project and one trade-off you made.' for s in (target or present)[:6]]
    questions += ['Tell me about a difficult bug and how you investigated it.','How would you verify an unexpected recruiter message?','Describe a team disagreement and how you handled it.']
    return {'role':role,'target_skills':target,'existing_skills':present,'missing_skills':missing,'stages':stages,'interview_questions':questions,
        'notice':'Rule-based starter roadmap, not a personalized labor-market prediction. Supply a job description for a closer match.' if target else 'Role not in the starter catalog. Add a job description containing technical skills.'}

def market(jobs):
    count=Counter()
    salaries=[]
    repeated=[];seen=set()
    for job in jobs:
        count.update(skills_in(job['description']))
        if job['salary']!='Not disclosed':
            salaries.append({'company':job['company'],'title':job['title'],'salary':job['salary'],'sources':job['links'],'type':'Advertised, unverified'})
        signature=(job['company'].lower(),job['title'].lower(),job['location'].lower())
        if signature in seen:
            repeated.append({'title':job['title'],'company':job['company'],'note':'Duplicate in this sample; not proof of a ghost job.'})
        seen.add(signature)
    return {'sample_count':len(jobs),'skills':[{'skill':s,'count':n} for s,n in count.most_common(12)],
        'salary_observations':salaries,'duplicates':repeated,
        'notice':'Counts come only from this search page. No comprehensive demand, fairness, salary-average or ghost-job conclusion is supported.'}
