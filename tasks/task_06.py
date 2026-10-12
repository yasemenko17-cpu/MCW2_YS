import re

def workflow_issues(wf: dict) -> list[str]:
    messages = []
    if not isinstance(wf, dict):
        return messages
        
    on_triggers = wf.get('on')
    if on_triggers is None:
        on_triggers = wf.get(True)
        
    is_pr_target = False
    if isinstance(on_triggers, str):
        is_pr_target = (on_triggers == 'pull_request_target')
    elif isinstance(on_triggers, list):
        is_pr_target = 'pull_request_target' in on_triggers
    elif isinstance(on_triggers, dict):
        is_pr_target = 'pull_request_target' in on_triggers
        
    top_permissions = 'permissions' in wf
    jobs = wf.get('jobs') or {}
    
    for job_name, job_conf in jobs.items():
        if not isinstance(job_conf, dict):
            job_conf = {}
            
        has_perm = top_permissions or ('permissions' in job_conf)
        if not has_perm:
            messages.append(f"{job_name}: немає permissions")
            
        needs = job_conf.get('needs')
        if needs:
            if isinstance(needs, str):
                needs_list = [needs]
            elif isinstance(needs, list):
                needs_list = needs
            else:
                needs_list = []
            for n in needs_list:
                if n not in jobs:
                    messages.append(f"{job_name}: needs посилається на невідому задачу {n}")
                    
        steps = job_conf.get('steps') or []
        for k, step in enumerate(steps, 1):
            if not isinstance(step, dict):
                continue
            uses = step.get('uses')
            run = step.get('run')
            
            if uses:
                if not uses.startswith('./') and not uses.startswith('docker://'):
                    if '@' not in uses:
                        messages.append(f"{job_name}, крок {k}: дію {uses} не закріплено")
                    else:
                        action_name, ref = uses.rsplit('@', 1)
                        if ref in ('main', 'master', 'latest'):
                            messages.append(f"{job_name}, крок {k}: дію {uses} не закріплено")
                            
            if run and isinstance(run, str):
                if re.search(r'\$\{\{\s*github\.event\.', run):
                    messages.append(f"{job_name}, крок {k}: вираз github.event у run")
                if re.search(r'\$\{\{\s*secrets\.', run):
                    messages.append(f"{job_name}, крок {k}: секрет напряму у run")
                    
            if is_pr_target and uses and uses.startswith('actions/checkout'):
                with_block = step.get('with') or {}
                ref_val = str(with_block.get('ref', ''))
                if 'github.event.pull_request.head' in ref_val:
                    messages.append(f"{job_name}, крок {k}: pull_request_target з checkout коду з PR")
                    
    return messages