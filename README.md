# Ansible Role: Harbor

Installs and manages [Harbor](https://goharbor.io/) using Harbor's supported installer flow:

- download the official installer bundle
- render `harbor.yml`
- run `install.sh` / `prepare`
- manage services through `docker compose` with a `docker-compose` fallback

This is a modernization of the original role, which used Harbor 1.x internals directly. The role now tracks Harbor's current layout much more closely and avoids deprecated Ansible Docker modules.

## Requirements

- Docker Engine installed on the target host
- `docker compose` v2 preferred, or `docker-compose` v1 as a fallback
- enough disk space for Harbor images and data

This role does not install Docker itself.

## Compatibility Notes

- The defaults target Harbor `2.15.0`.
- The role keeps old variable names such as `harbor_ui_url_protocol`, `harbor_exposed_http_port`, `harbor_exposed_https_port`, `harbor_behind_proxy`, and `harbor_registry_realm_protocol` so older playbooks keep working with minimal changes.
- Direct in-place upgrades from very old `harbor.cfg`-based installs are blocked by default. Harbor's upstream upgrade path across major versions is multi-step, so the role fails fast unless you explicitly set `harbor_allow_unsupported_upgrade: true`.
- Optional installer extras are still passed through via `harbor_extras`, but only extras supported by the chosen Harbor version will work. On current Harbor that usually means `trivy` and `notary`.

## Role Variables

For the full list, see `defaults/main.yaml`.

Common variables:

```yaml
harbor_version: 2.15.0
harbor_install_dir: /opt
harbor_datadir: /data
harbor_hostname: registry.example.com
harbor_ui_url_protocol: http
harbor_exposed_http_port: 80
harbor_exposed_https_port: 443
```

Switch to HTTPS:

```yaml
harbor_ui_url_protocol: https
harbor_ssl_cert_self_sign: true
```

If you already have certificates:

```yaml
harbor_ui_url_protocol: https
harbor_ssl_cert_self_sign: false
harbor_ssl_cert: /etc/pki/harbor/fullchain.pem
harbor_ssl_cert_key: /etc/pki/harbor/privkey.pem
```

To run Harbor behind another proxy or load balancer:

```yaml
harbor_hostname: registry.example.com
harbor_behind_proxy: true
harbor_registry_realm_protocol: https
harbor_external_url: https://registry.example.com

# Harbor itself can still listen on HTTP internally
harbor_ui_url_protocol: http
harbor_exposed_http_port: 8080
```

To enable installer extras:

```yaml
harbor_extras:
  - trivy
  - notary
```

Advanced Harbor configuration can be passed through with dictionaries that are rendered directly into `harbor.yml`:

```yaml
harbor_storage_service:
  filesystem:
    maxthreads: 100

harbor_external_database:
  harbor:
    host: db.example.com
    port: 5432
    db_name: registry
    username: harbor
    password: supersecret
    ssl_mode: disable
```

## Bootstrap Projects And Users

Projects are created through Harbor's `v2.0` API after the installation is ready:

```yaml
harbor_projects:
  - project_name: apps
    is_public: false
```

Users can also be created automatically. Disable self-registration first:

```yaml
harbor_self_registration: "off"
harbor_users:
  - username: deployer
    email: deployer@example.com
    realname: CI Deployer
    has_admin_role: false
```

Project creation intentionally sticks to the most stable fields (`project_name` and visibility) so it works cleanly across Harbor 2.x releases.

## Example Playbook

```yaml
---
- name: Install Harbor
  hosts: registry
  roles:
    - role: nicholasamorim.harbor
      vars:
        harbor_hostname: registry.example.com
        harbor_ui_url_protocol: https
        harbor_ssl_cert_self_sign: true
        harbor_extras:
          - trivy
```

## Managing Harbor State

The role still supports `tasks_from` for service control:

```yaml
---
- hosts: registry
  tasks:
    - name: Restart Harbor
      include_role:
        name: harbor
        tasks_from: restart
```

Available task files are `start`, `stop`, and `restart`.

## Testing

This repository now includes two GitHub Actions workflows:

- `CI` runs on pushes and pull requests and covers `yamllint`, `ansible-lint`, syntax-checking, and Molecule scenarios for the happy path, HTTPS self-signed configuration, the legacy upgrade guard, and the lifecycle task files.
- `Integration` is a manual smoke test that runs the role against a real `ubuntu-latest` runner with Docker and Harbor's online installer. It is separate so normal PR validation stays fast and cheap on the free plan.

Local test entry points:

```bash
python -m pip install -r requirements-test.txt "ansible-core==2.19.*"
yamllint .
ansible-lint
molecule test -s default
```

## Notes

- `harbor_api_url` defaults to `{{ harbor_external_url }}/api/v2.0`.
- When the role generates a self-signed certificate, API bootstrap calls default to `validate_certs: false`. Set `harbor_api_validate_certs: true` if your certificate chain is trusted on the target host.
- The role intentionally avoids patching generated Harbor files after installation; changes should go through `harbor.yml` inputs instead.
