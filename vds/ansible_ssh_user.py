import os

from vars import USER


def change_ansible_ssh_user(inventory_file: str, new_ssh_user: str):
    with open(inventory_file, 'r') as file:
        lines = file.readlines()

    in_all_vars_section = False
    updated = False
    new_lines = []

    for line in lines:
        if line.strip() == '[all:vars]':
            in_all_vars_section = True
        elif line.startswith('[') and in_all_vars_section:
            in_all_vars_section = False
            updated = False

        if in_all_vars_section:
            if line.startswith('ansible_ssh_user'):
                if not updated:
                    new_lines.append(f"ansible_ssh_user={new_ssh_user}\n")
                    updated = True
                continue
            elif line.startswith('new_user'):
                continue
        new_lines.append(line)

    with open(inventory_file, 'w') as file:
        file.writelines(new_lines)


if __name__ == '__main__':
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    inventory_path = os.path.join(project_root, 'ansible', 'inventory')
    hosts_file_path = os.path.join(inventory_path, 'hosts')
    change_ansible_ssh_user(hosts_file_path, USER)
