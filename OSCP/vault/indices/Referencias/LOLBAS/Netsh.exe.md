# LOLBAS: Netsh.exe

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Netsh is a Windows tool used to manipulate network interface settings.

## Comandos

### Proxy execution of .dll

Execute · priv: Admin · T1546.007

```cmd
netsh.exe add helper {PATH_ABSOLUTE:.dll}
```

Use Netsh in order to execute a .dll file and also gain persistence, every time the netsh command is called

