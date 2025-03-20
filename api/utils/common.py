def split_domain(domain):
    domain_parts = domain.split('.')
    if len(domain_parts) >= 2:
        sub_domain = '.'.join(domain_parts[:-2]) if len(domain_parts) > 2 else '@'
        main_domain = '.'.join(domain_parts[-2:])
    return sub_domain, main_domain