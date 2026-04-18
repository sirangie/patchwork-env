# patchwork-env

> A CLI tool to diff and sync `.env` files across environments without leaking secrets.

---

## Installation

```bash
pip install patchwork-env
```

Or with pipx for isolated installs:

```bash
pipx install patchwork-env
```

---

## Usage

**Diff two `.env` files** to see what keys are missing or mismatched (values are masked):

```bash
patchwork-env diff .env.example .env.production
```

**Sync missing keys** from a template into a target environment file:

```bash
patchwork-env sync .env.example .env.local
```

**Check for missing keys** without making changes:

```bash
patchwork-env check .env.example .env.staging
```

Example output:

```
[+] DB_HOST      missing in .env.staging
[~] API_URL      key exists, value differs
[✓] SECRET_KEY   present in both
```

Secrets are never printed — only key names and status are shown.

---

## Why patchwork-env?

Managing `.env` files across dev, staging, and production is error-prone. `patchwork-env` helps you catch missing or drifted configuration keys early, without ever exposing sensitive values in your terminal or logs.

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any major changes.

---

## License

[MIT](LICENSE)