# TODO убрать new_user, заменить root на new_user в hosts
def change_ansible_ssh_user(inventory_file: str, new_ssh_user: str):
    with open(inventory_file, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if line.strip() == '[all:vars]':
            for j in range(i + 1, len(lines)):
                if not lines[j].strip() or lines[j].startswith('['):
                    break
                key, value = lines[j].strip().split('=')
                if key == 'ansible_ssh_user':
                    lines[j] = f"{key}={new_ssh_user}\n"

    with open(inventory_file, 'w') as f:
        f.writelines(lines)
