# LOLBAS: Cdb.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Debugging tool included with Windows Debugging Tools.

## Comandos

### Local execution of assembly shellcode.

Execute · priv: User · T1127

```cmd
cdb.exe -cf {PATH:.wds} -o notepad.exe
```

Launch 64-bit shellcode from the specified .wds file using cdb.exe.

### Run a shell command under a trusted Microsoft signed binary

Execute · priv: User · T1127

```cmd
cdb.exe -pd -pn {process_name}
.shell {CMD}
```

Attaching to any process and executing shell commands.

### Run commands under a trusted Microsoft signed binary

Execute · priv: User · T1127

```cmd
cdb.exe -c {PATH:.txt} "{CMD}"
```

Execute arbitrary commands and binaries using a debugging script (see Resources section for a sample file).

