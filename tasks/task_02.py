def compose_issues(compose: dict) -> list[str]:
    messages = []
    if not isinstance(compose, dict):
        return messages
    services = compose.get('services') or {}
    top_volumes = compose.get('volumes') or {}
    
    port_registry = {} # (host_port, proto): service_name

    for s_name, s_conf in services.items():
        if not isinstance(s_conf, dict):
            s_conf = {}
        
        # 1. Перевірка томів
        volumes = s_conf.get('volumes') or []
        reported_vols = set()
        for v in volumes:
            if not isinstance(v, str):
                continue
            parts = v.split(':')
            if len(parts) < 2:
                continue
            src = parts[0]
            if src.startswith('/') or src.startswith('.'):
                continue
            if src not in top_volumes and src not in reported_vols:
                reported_vols.add(src)
                messages.append(f"{s_name}: том {src} не оголошено")

        # 2. Перевірка залежностей
        deps = s_conf.get('depends_on') or {}
        if isinstance(deps, list):
            dep_list = [(d, {}) for d in deps]
        elif isinstance(deps, dict):
            dep_list = []
            for d_name, d_opts in deps.items():
                if d_opts is None:
                    d_opts = {}
                dep_list.append((d_name, d_opts))
        else:
            dep_list = []

        for d_name, d_opts in dep_list:
            if d_name not in services:
                messages.append(f"{s_name}: залежність {d_name} не знайдено")
            else:
                cond = d_opts.get('condition')
                if cond == 'service_healthy':
                    target_conf = services[d_name]
                    if not isinstance(target_conf, dict) or 'healthcheck' not in target_conf:
                        messages.append(f"{s_name}: залежність {d_name} чекає service_healthy, але у {d_name} немає healthcheck")

        # 3. Перевірка портів
        ports = s_conf.get('ports') or []
        for p in ports:
            p_str = str(p)
            if '/' in p_str:
                p_parts = p_str.split('/')
                port_part = p_parts[0]
                proto = p_parts[1]
            else:
                port_part = p_str
                proto = 'tcp'
            
            p_subparts = port_part.split(':')
            if len(p_subparts) < 2:
                continue
            host_port = p_subparts[-2]
            
            key = (host_port, proto)
            if key in port_registry:
                first_serv = port_registry[key]
                messages.append(f"{s_name}: порт хоста {host_port} уже зайнято сервісом {first_serv}")
            else:
                port_registry[key] = s_name

    return messages