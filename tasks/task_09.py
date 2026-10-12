import re
import fnmatch

def dockerfile_build_plan(text: str, changed: list[str]) -> dict:
    lines = text.splitlines()
    
    raw_instructions = []
    i = 0
    n = len(lines)
    while i < n:
        line_num = i + 1
        curr_line = lines[i].strip()
        
        if not curr_line or curr_line.startswith('#'):
            i += 1
            continue
            
        parts = [curr_line]
        while parts[-1].endswith('\\') and i + 1 < n:
            parts[-1] = parts[-1][:-1].strip()
            i += 1
            next_line = lines[i].strip()
            parts.append(next_line)
            
        full_text = " ".join(p for p in parts if p)
        if not full_text or full_text.startswith('#'):
            i += 1
            continue
            
        tokens = full_text.split()
        if tokens:
            instr_name = tokens[0].upper()
            raw_instructions.append((line_num, instr_name, full_text))
        i += 1
        
    from_indices = [idx for idx, (_, name, _) in enumerate(raw_instructions) if name == 'FROM']
    if not from_indices:
        raise ValueError("Немає інструкції FROM")
        
    first_from_idx = from_indices[0]
    instructions = raw_instructions[first_from_idx:]
    
    stages = []
    stage_names_map = {}
    errors = []
    
    current_stage_instructions = []
    stage_list = []
    
    stage_idx = 0
    for line_num, name, text_line in instructions:
        if name == 'FROM':
            if current_stage_instructions:
                stage_list.append(current_stage_instructions)
                current_stage_instructions = []
            
            tokens = text_line.split()[1:]
            non_flag_tokens = [t for t in tokens if not t.startswith('--')]
            base_image = non_flag_tokens[0] if non_flag_tokens else ""
                
            stage_name = str(stage_idx)
            text_upper = text_line.upper()
            if ' AS ' in text_upper:
                parts = re.split(r'\s+AS\s+', text_line, flags=re.IGNORECASE)
                if len(parts) > 1:
                    stage_name = parts[1].split()[0].lower()
                    
            if stage_name in stage_names_map:
                errors.append((line_num, f"рядок {line_num}: ім'я етапу {stage_name} уже використано"))
            else:
                stage_names_map[stage_name] = stage_idx
                
            stages.append((stage_name, base_image))
            current_stage_instructions.append((line_num, name, text_line, base_image))
            stage_idx += 1
        else:
            current_stage_instructions.append((line_num, name, text_line, None))
            
    if current_stage_instructions:
        stage_list.append(current_stage_instructions)
        
    stage_deps = {i: set() for i in range(len(stages))}
    
    for s_idx, st_instrs in enumerate(stage_list):
        for line_num, name, text_line, base_img in st_instrs:
            ref_target = None
            if name == 'FROM':
                if base_img and base_img.lower() in stage_names_map:
                    ref_target = base_img.lower()
            elif name in ('COPY', 'ADD'):
                match_from = re.search(r'--from=([^\s]+)', text_line)
                if match_from:
                    ref_target = match_from.group(1).lower()
                    
            if ref_target:
                if ref_target in stage_names_map:
                    target_idx = stage_names_map[ref_target]
                    if target_idx >= s_idx:
                        errors.append((line_num, f"рядок {line_num}: --from={ref_target} посилається на етап, якого ще немає"))
                    else:
                        stage_deps[s_idx].add(target_idx)
                elif ref_target.isdigit():
                    target_idx = int(ref_target)
                    if target_idx >= s_idx:
                        errors.append((line_num, f"рядок {line_num}: --from={ref_target} посилається на етап, якого ще немає"))
                    else:
                        stage_deps[s_idx].add(target_idx)

    errors.sort(key=lambda x: x[0])
    error_messages = [msg for _, msg in errors]
    
    last_stage_idx = len(stages) - 1
    depended_on = {last_stage_idx}
    queue = [last_stage_idx]
    while queue:
        curr = queue.pop(0)
        for prev in stage_deps[curr]:
            if prev not in depended_on:
                depended_on.add(prev)
                queue.append(prev)
                
    unused_stages = []
    for idx, (s_name, _) in enumerate(stages):
        if idx != last_stage_idx and idx not in depended_on:
            unused_stages.append(s_name)
            
    def matches_changed(src):
        if not changed:
            return False
        if src.startswith('./'):
            src = src[2:]
        if src == '.':
            return True
            
        for f in changed:
            if f.startswith('./'):
                f = f[2:]
            if f == src or f.startswith(src.rstrip('/') + '/'):
                return True
            if fnmatch.fnmatchcase(f, src):
                return True
        return False

    invalidated_lines = set()
    stage_invalidated = {}
    
    for s_idx, st_instrs in enumerate(stage_list):
        if s_idx not in depended_on and s_idx != last_stage_idx:
            continue
            
        base_inv = False
        _, _, from_text, base_img = st_instrs[0]
        
        if base_img and base_img.lower() in stage_names_map:
            b_idx = stage_names_map[base_img.lower()]
            if stage_invalidated.get(b_idx, False):
                base_inv = True
                
        if base_inv:
            stage_invalidated[s_idx] = True
            for line_num, _, _, _ in st_instrs:
                invalidated_lines.add(line_num)
            continue
            
        prev_inv = False
        st_has_inv = False
        
        for idx_instr, (line_num, name, text_line, _) in enumerate(st_instrs):
            if idx_instr == 0:
                continue
                
            inv = prev_inv
            if name in ('COPY', 'ADD'):
                match_from = re.search(r'--from=([^\s]+)', text_line)
                if match_from:
                    from_val = match_from.group(1).lower()
                    t_idx = stage_names_map.get(from_val)
                    if t_idx is None and from_val.isdigit():
                        t_idx = int(from_val)
                    if t_idx is not None and stage_invalidated.get(t_idx, False):
                        inv = True
                else:
                    tokens = text_line.split()[1:]
                    sources = [t for t in tokens if not t.startswith('--')]
                    if sources:
                        srcs = sources[:-1]
                        for src in srcs:
                            if matches_changed(src):
                                inv = True
                                break
                                
            if inv:
                invalidated_lines.add(line_num)
                prev_inv = True
                st_has_inv = True
            else:
                prev_inv = False
                
        if st_has_inv:
            stage_invalidated[s_idx] = True
            
    rebuilt_list = sorted(list(invalidated_lines))
    
    return {
        "stages": stages,
        "errors": error_messages,
        "unused": unused_stages,
        "rebuilt": rebuilt_list
    }