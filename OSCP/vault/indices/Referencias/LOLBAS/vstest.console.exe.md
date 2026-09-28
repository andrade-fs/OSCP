# LOLBAS: vstest.console.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `AWL Bypass`

VSTest.Console.exe is the command-line tool to run tests

## Comandos

### Proxy Execution and AWL bypass, Adversaries may run malicious code embedded inside the test methods of crafted dll/exe

AWL Bypass · priv: User · T1127

```cmd
vstest.console.exe {PATH:.dll}
```

VSTest functionality may allow an adversary to executes their malware by wrapping it as a test method then build it to a .exe or .dll file to be later run by vstest.console.exe. This may both allow AWL bypass or defense bypass in general

