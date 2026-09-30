"""Fill the profile banner's star count from the collected GitHub state."""

STAR_MARKER = "<!--total-stars-->"


def render_banner(template: str, total_stars: int) -> str:
    if STAR_MARKER not in template:
        raise ValueError("banner template is missing the total-stars marker")
    return template.replace(STAR_MARKER, f"{total_stars:,} ")
