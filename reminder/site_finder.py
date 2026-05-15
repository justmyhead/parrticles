import json
import anthropic


def find_new_site(liked: list[dict], disliked: list[dict], already_sent: list[str]) -> dict:
    client = anthropic.Anthropic()

    liked_lines = "\n".join(f"- {s['url']} ({s['title']})" for s in liked) or "None yet"
    disliked_lines = "\n".join(f"- {s['url']} ({s['title']})" for s in disliked) or "None yet"
    sent_lines = "\n".join(f"- {u}" for u in already_sent) or "None yet"

    prompt = f"""You are a curator of cutting-edge, weird, and experimental design on the web.

Suggest ONE site for a design-curious person to explore today. Prioritise:
- Personal portfolios with unconventional or extreme aesthetics
- Net art, web art, and interactive browser experiments
- Generative / data-driven visual work
- Brutalist, glitchy, maximalist, or radically minimal sites
- Underground or niche design scenes, zines, or collectives
- Sites where the medium IS the message — the website itself is the art

Never suggest: agency marketing sites, design award aggregators (Awwwards, Behance), mainstream news or blogs, or anything primarily selling a product.

User LIKED these — lean toward similar vibes:
{liked_lines}

User DISLIKED these — find something genuinely different:
{disliked_lines}

Already sent — never repeat:
{sent_lines}

Reply with ONLY a JSON object, no markdown fences:
{{"url": "https://...", "title": "Site Name", "description": "2-3 sentences on what makes this site worth visiting and what's weird or special about it."}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    # Strip markdown code fences if the model adds them anyway
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()

    return json.loads(text)
