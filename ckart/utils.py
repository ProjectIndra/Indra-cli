
def resolve_prefix(items, user_input, key):
    """
    Returns (matched_item, error_message).
    Matches user_input against the start of the string in items[key].
    """
    matches = [item for item in items if item.get(key, "").startswith(user_input)]
    
    if not matches:
        return None, f"No ID found starting with '{user_input}'."
    
    if len(matches) > 1:
        # Check for exact match to break ties
        exact = [m for m in matches if m.get(key) == user_input]
        if len(exact) == 1:
            return exact[0], None
            
        options = ", ".join([m.get(key)[:8] for m in matches[:5]])
        return None, f"Multiple IDs match '{user_input}': {options}..."
        
    return matches[0], None
