# Ansible Role: Harbor

An Ansible Role that installs [Harbor](https://github.com/goharbor/harbor) on Linux.

This role is in alpha stage. Issues and PRs are welcome.

## Requirements

None.

## Role Variables

For a complete list see `defaults/main.yaml`.

By default, the role uses the IP of the current host to set `harbor_hostname`. You can override it.

To change the install dir:

```yaml
harbor_install_dir: /opt
```

To change default protocol:

```yaml
harbor_ui_url_protocol: "http"
```

If you want to change the exposed ports of Harbor's NGINX from the defaults of 80 and 443, use:

```yaml
harbor_exposed_http_port: 81
harbor_exposed_https_port: 444
```

To install with extras set:

```yaml
harbor_extras:
    - clair
    - notary
```

You can also pass extra arguments to the installer with `harbor_installer_extra_args` (a string).

You may define `harbor_projects` if you want projects to be automatically created once harbor is installed.

```yaml
harbor_projects:
  - project_name: test
    is_public: "false"
    content_trust: "false"
    prevent_vul: "true"
    severity: "high"
    auto_scan: "true"
```


By default, users can self-register. If you prefer to create users automatically, you _must_ disable self-registration and set a list of users. Those users will be created automatically. The password defaults to "HarborUser12345".

This operation is idempotent.

```yaml
harbor_self_registration: "off"
harbor_users:
    - username: user1
      email: user1@test.com
      realname: User Number 1
      role_name: developer
      role_id: 2
      has_admin_role: true
```

## Dependencies

None.

## Example Playbook

```yaml
---
- name: Installing and configuring Harbor
  hosts: registry
  vars:
    harbor_projects:
      - project_name: myproject
        is_public: "false"
        content_trust: "false"
        prevent_vul: "true"
        severity: "high"
        auto_scan: "true"
    harbor_users:
      - username: user1
        email: user1@test.com
        realname: User Number 1
        role_name: developer
        role_id: 2
        has_admin_role: true
  roles:
    - harbor
```

After the playbook runs, you should be able to navigate to your host on port 80/443 and see Harbor's UI. You can login with `admin/Harbor12345`. If you changed the exposed ports, remember to use them instead of 80/443.

For convenience, this role includes tasks to stop, start and restart the registry using docker-compose.

Here's a playbook created specifically to restart the registry:

```yaml
---
- hosts: registry
  tasks:
    - name: Restarting Harbor
      include_role:
        name: harbor
        tasks_from: restart


```

Running the playbook above effectively restarts all components of Harbor. This takes into consideration if you are using `clair` and/or `notary` and uses their docker-compose files too.

`tasks_from` can be `restart`, `start` and `stop`.

If you are running the playbook again to ensure the list of users but you have already changed the default admin password, you can set the `harbor_admin_password` variable somewhere or simply pass it in the command-line with `-e "harbor_admin_password=mypass"`.

## Author Information

This role was created in 2019 by [Nicholas Amorim](https://github.com/nicholasamorim).
