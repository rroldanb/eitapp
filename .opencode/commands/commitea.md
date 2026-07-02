---
description: Commit autodescriptivo con selección + push
---

1. Ejecutá `git status` y `git diff` para inspeccionar los cambios sin staged
2. Si **no hay nada para commitear** (no hay cambios staged ni unstaged ni untracked), respondé: "No hay nada para commitear" y abortá el comando
3. Si hay cambios, generá **4 opciones** de mensaje de commit en español, **máximo 60 caracteres cada una**, que describan distintos aspectos de los cambios detectados en el diff
4. Usá la herramienta `question` para presentar las opciones al usuario con:
   - Opciones 1 a 4: los mensajes generados
   - Opción 5: "Ingresar propia" con descripción "Escribir mi propio mensaje"
   - Opción 6: "Cancelar" con descripción "Abortar el commit"
5. Si el usuario selecciona un mensaje (1-4), usalo tal cual
6. Si selecciona "Ingresar propia", pedí que escriba el mensaje y validá que no exceda 60 caracteres. Si lo excede, pedí que lo acorte
7. Si selecciona "Cancelar", abortá el comando sin ejecutar nada
8. Ejecutá secuencialmente:
   - `git add .`
   - `git commit -m "<mensaje>"`
   - `git push`
9. Si **cualquier paso falla** (git add, commit, o push), mostrá el error completo al usuario y **no continués** con los pasos siguientes. Indicá claramente qué paso falló y por qué

No ejecutes ningún paso sin la aprobación explícita del usuario.
