def reflect_attrs(child, parent):
    """Composition Magic: reflect all missing parents attributes into child."""
    existing = dir(child)
    for attr in dir(parent):
        if attr not in existing:
            child.__dict__[attr] = getattr(parent, attr)
