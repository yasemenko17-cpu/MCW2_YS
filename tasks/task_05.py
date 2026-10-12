def plan_summary(changes: list[dict], protected: tuple = ()) -> dict:
    valid_actions = {
        ('no-op',): 'no-op',
        ('read',): 'read',
        ('create',): 'create',
        ('update',): 'update',
        ('delete',): 'delete',
        ('delete', 'create'): 'replace',
        ('create', 'delete'): 'replace'
    }
    
    add_count = 0
    change_count = 0
    destroy_count = 0
    replace_list = []
    blocked_list = []
    by_type = {}
    
    for ch in changes:
        addr = ch.get('address', '')
        r_type = ch.get('type', '')
        actions = tuple(ch.get('actions', []))
        
        if actions not in valid_actions:
            actions_str = ", ".join(actions)
            raise ValueError(f"Невідома дія: {actions_str} для {addr}")
            
        act_type = valid_actions[actions]
        
        if act_type == 'no-op' or act_type == 'read':
            continue
            
        if r_type not in by_type:
            by_type[r_type] = {"add": 0, "change": 0, "destroy": 0}
            
        if act_type == 'create':
            add_count += 1
            by_type[r_type]["add"] += 1
        elif act_type == 'update':
            change_count += 1
            by_type[r_type]["change"] += 1
        elif act_type == 'delete':
            destroy_count += 1
            by_type[r_type]["destroy"] += 1
            if r_type in protected:
                blocked_list.append(addr)
        elif act_type == 'replace':
            add_count += 1
            destroy_count += 1
            replace_list.append(addr)
            by_type[r_type]["add"] += 1
            by_type[r_type]["destroy"] += 1
            if r_type in protected:
                blocked_list.append(addr)
                
    filtered_by_type = {
        t: counts for t, counts in by_type.items()
        if counts["add"] > 0 or counts["change"] > 0 or counts["destroy"] > 0
    }
    
    if add_count == 0 and change_count == 0 and destroy_count == 0:
        line = "No changes."
    else:
        line = f"Plan: {add_count} to add, {change_count} to change, {destroy_count} to destroy."
        
    return {
        "add": add_count,
        "change": change_count,
        "destroy": destroy_count,
        "replace": replace_list,
        "blocked": blocked_list,
        "by_type": filtered_by_type,
        "line": line
    }