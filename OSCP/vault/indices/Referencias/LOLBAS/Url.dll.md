# LOLBAS: Url.dll

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[LOLBAS|Índice LOLBAS]]

> Fuente: [https://lolbas-project.github.io/](https://lolbas-project.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

LOLBAS — binarios legitimos de Windows usables como atacante (living off the land).

**Categorías:** `Execute`

Internet Shortcut Shell Extension DLL.

## Comandos

### Invoke an HTML Application via mshta.exe (Default Handler).

Execute · priv: User · T1218.011

```cmd
rundll32.exe url.dll,OpenURL {PATH_ABSOLUTE:.hta}
```

Launch a HTML application payload by calling OpenURL.

### Load an executable payload by calling a .url file.

Execute · priv: User · T1218.011

```cmd
rundll32.exe url.dll,OpenURL {PATH_ABSOLUTE:.url}
```

Launch an executable payload via proxy through a .url (information) file by calling OpenURL.

### Load an executable payload by specifying the file protocol handler (obfuscated).

Execute · priv: User · T1218.011

```cmd
rundll32.exe url.dll,OpenURL file://^C^:^/^W^i^n^d^o^w^s^/^s^y^s^t^e^m^3^2^/^c^a^l^c^.^e^x^e
```

Launch an executable by calling OpenURL.

### Launch an executable.

Execute · priv: User · T1218.011

```cmd
rundll32.exe url.dll,FileProtocolHandler {PATH_ABSOLUTE:.exe}
```

Launch an executable by calling FileProtocolHandler.

### Load an executable payload by specifying the file protocol handler (obfuscated).

Execute · priv: User · T1218.011

```cmd
rundll32.exe url.dll,FileProtocolHandler file://^C^:^/^W^i^n^d^o^w^s^/^s^y^s^t^e^m^3^2^/^c^a^l^c^.^e^x^e
```

Launch an executable by calling FileProtocolHandler.

### Invoke an HTML Application via mshta.exe (Default Handler).

Execute · priv: User · T1218.011

```cmd
rundll32.exe url.dll,FileProtocolHandler file:///C:/test/test.hta
```

Launch a HTML application payload by calling FileProtocolHandler.

