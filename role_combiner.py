import discord

# ── Config ────────────────────────────────────────────────────────────────────

TOKEN = "MTUwNDg4NjE0Mjg3NTYwMzA1NA.GnvU5E.2EG1MgPVhxRM0R4z0kieMZj-tcx7C-Y7b3IlHs"

YEAR_ROLES  = {"2026-grads", "2027-grads", "2028-grads", "2029-grads"}
MAJOR_ROLES = {"software-eng", "engineering", "business"}

# Explicit map: (major_role, year_role) → combined role name
# Edit this table if role names ever change
ROLE_MAP = {
    ("software-eng", "2026-grads"): "swe-2026",
    ("software-eng", "2027-grads"): "swe-2027",
    ("software-eng", "2028-grads"): "swe-2028",
    ("software-eng", "2029-grads"): "swe-2029-and-beyond",

    ("business",     "2026-grads"): "business-2026",
    ("business",     "2027-grads"): "business-2027",
    ("business",     "2028-grads"): "business-2028",
    ("business",     "2029-grads"): "business-2029-and-beyond",

    ("engineering",  "2026-grads"): "engineering-2026",
    ("engineering",  "2027-grads"): "engineering-2027",
    ("engineering",  "2028-grads"): "engineering-2028",
    ("engineering",  "2029-grads"): "engineering-2029-and-beyond",
}

# All valid combined role names — used to clean up stale roles
COMBINED_ROLES = set(ROLE_MAP.values())

# ── Bot setup ─────────────────────────────────────────────────────────────────

intents = discord.Intents.default()
intents.members = True          # Enable in Discord Developer Portal too

client = discord.Client(intents=intents)

# ── Events ────────────────────────────────────────────────────────────────────

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    for guild in client.guilds:
        print(f"Watching server: {guild.name} ({guild.id}) — {guild.member_count} members")

@client.event
async def on_member_update(before, after):
    print(f"Role change detected for {after.display_name}")
    print(f"  Current roles: {[r.name for r in after.roles]}")
    # Only run if roles actually changed
    if before.roles == after.roles:
        return

    # Find which roles were added or removed in this event
    added   = {r.name for r in after.roles}  - {r.name for r in before.roles}
    removed = {r.name for r in before.roles} - {r.name for r in after.roles}
    changed = added | removed

    # Ignore events caused by the bot itself assigning combined roles
    if changed and all(c in COMBINED_ROLES for c in changed):
        return

    guild      = after.guild
    role_names = {r.name for r in after.roles}

    # Match roles by checking if the name ends with the key — ignores emoji prefixes
    year_role  = next((y for y in YEAR_ROLES  if any(rn.endswith(y) for rn in role_names)), None)
    major_role = next((m for m in MAJOR_ROLES if any(rn.endswith(m) for rn in role_names)), None)

    # Remove any stale combined roles
    stale = [r for r in after.roles if r.name in COMBINED_ROLES]
    if stale:
        await after.remove_roles(*stale)

    # Look up and assign the correct combined role
    if year_role and major_role:
        combined_name = ROLE_MAP.get((major_role, year_role))

        if combined_name:
            combined_role = discord.utils.get(guild.roles, name=combined_name)

            if combined_role:
                await after.add_roles(combined_role)
                print(f"✓ Assigned '{combined_name}' to {after.display_name}")
            else:
                print(f"✗ Role '{combined_name}' not found in server — create it first")

client.run(TOKEN)
