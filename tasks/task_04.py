import re

def parse_exposition(text: str) -> list[tuple[str, dict, float]]:
    results = []
    seen_series = set()
    
    lines = text.splitlines()
    for idx, raw_line in enumerate(lines, 1):
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
            
        match = re.match(r'^([a-zA-Z_:][a-zA-Z0-9_]*)(?:(\{.*\}))?\s+(.+)$', line)
        if not match:
            raise ValueError(f"Некоректний рядок {idx}: {line}")
            
        m_name, labels_str, tail = match.groups()
        
        labels = {}
        if labels_str:
            content = labels_str[1:-1].strip()
            if content:
                i = 0
                n = len(content)
                while i < n:
                    while i < n and (content[i].isspace() or content[i] == ','):
                        i += 1
                    if i >= n:
                        break
                    m_lbl = re.match(r'[a-zA-Z_][a-zA-Z0-9_]*', content[i:])
                    if not m_lbl:
                        raise ValueError(f"Некоректний рядок {idx}: {line}")
                    lbl_name = m_lbl.group(0)
                    i += len(lbl_name)
                    
                    while i < n and content[i].isspace():
                        i += 1
                    if i >= n or content[i] != '=':
                        raise ValueError(f"Некоректний рядок {idx}: {line}")
                    i += 1
                    
                    while i < n and content[i].isspace():
                        i += 1
                    if i >= n or content[i] != '"':
                        raise ValueError(f"Некоректний рядок {idx}: {line}")
                    i += 1
                    
                    val_chars = []
                    escaped = False
                    closed = False
                    while i < n:
                        ch = content[i]
                        if escaped:
                            if ch in ('\\', '"', 'n'):
                                if ch == 'n':
                                    val_chars.append('\n')
                                else:
                                    val_chars.append(ch)
                            else:
                                raise ValueError(f"Некоректний рядок {idx}: {line}")
                            escaped = False
                        elif ch == '\\':
                            escaped = True
                        elif ch == '"':
                            closed = True
                            i += 1
                            break
                        else:
                            val_chars.append(ch)
                        i += 1
                    if not closed or escaped:
                        raise ValueError(f"Некоректний рядок {idx}: {line}")
                        
                    if lbl_name in labels:
                        raise ValueError(f"Некоректний рядок {idx}: {line}")
                    labels[lbl_name] = "".join(val_chars)
                    
                    while i < n and (content[i].isspace() or content[i] == ','):
                        i += 1

        tail_parts = tail.split()
        if len(tail_parts) > 2 or len(tail_parts) == 0:
            raise ValueError(f"Некоректний рядок {idx}: {line}")
            
        val_str = tail_parts[0]
        if len(tail_parts) == 2:
            ts_str = tail_parts[1]
            if not ts_str.isdigit():
                raise ValueError(f"Некоректний рядок {idx}: {line}")
                
        try:
            if val_str.lower() in ('inf', '+inf'):
                val = float('inf')
            elif val_str.lower() == '-inf':
                val = float('-inf')
            else:
                val = float(val_str)
        except ValueError:
            raise ValueError(f"Некоректний рядок {idx}: {line}")
            
        series_key = (m_name, tuple(sorted(labels.items())))
        if series_key in seen_series:
            raise ValueError(f"Дублікат ряду у рядку {idx}: {line}")
        seen_series.add(series_key)
        
        results.append((m_name, labels, val))
        
    return results