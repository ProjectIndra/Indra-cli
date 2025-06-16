import os


def load_env(env_file=".env"):
    if os.path.exists(env_file):
        with open(
            env_file, "r", encoding="utf-8-sig"
        ) as f:  # utf-8-sig removes BOM if present
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"')
                # print(f"[+] Setting environment variable: {key}={value}")
                os.environ[key] = value


def set_persistent_env_var(key, value, env_file=".env"):
    """
    Set or update an environment variable in a project-specific .env file.
    The change does not persist globally but can be sourced manually.
    """
    print("setting persistent env var in", env_file)
    lines = []
    updated = False

    # Read existing .env file if it exists
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8-sig") as f:
            for l in f:
                if l.strip().startswith(f"{key}="):
                    lines.append(f'{key}="{value}"\n')  # Update existing key
                    updated = True
                else:
                    lines.append(l)

    if not updated:
        lines.append(f'\n{key}="{value}"\n')  # Add new key if missing

    # Write back to .env file
    with open(env_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # now update the environment variable
    load_env(env_file)

    print(f"[+] Successfully set {key} in {env_file}.")
