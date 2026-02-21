import os

files_to_fix = [
    'candidatos/templates/candidatos/home.html',
    'candidatos/templates/candidatos/comparar.html'
]

for file_path in files_to_fix:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replacements explicitly
    content = content.replace('filtro_posicion==value', 'filtro_posicion == value')
    content = content.replace('filtro_partido==partido.id', 'filtro_partido == partido.id')
    content = content.replace('c.id==slots.0', 'c.id == slots.0')
    content = content.replace('c.id==slots.1', 'c.id == slots.1')
    content = content.replace('c.id==slots.2', 'c.id == slots.2')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Done fixing templates.")
