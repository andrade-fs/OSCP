# Chuleta — Active Directory avanzado (más allá de OSCP)

> Fuente: [The Hacker Recipes — AD Movement](https://www.thehacker.recipes/ad/movement).
> **Aviso de alcance**: varias de estas técnicas **superan el temario del OSCP/PEN-200**. Están
> aquí como referencia para practice labs, retos y para reconocerlas. En el examen, el camino
> estándar es `05-active-directory.md`.
>
> El vault ya cubre: Kerberoasting, AS-REP roast, spray, ACLs, delegaciones (un/constrained/RBCD),
> Shadow Credentials, ADCS ESC1-15, DCSync, Golden/Silver, Zerologon, persistencia básica.

---

## 1. Tickets forjados (stealth)

| Técnica | Idea | Diferencia |
| --- | --- | --- |
| **Golden ticket** | PAC forjado desde cero con el hash del `krbtgt` | detectable (no hay AS_REQ previo) |
| **Silver ticket** | tique de servicio forjado con la clave del servicio | detectable |
| **Diamond ticket** | se pide un **tique legítimo** y se **modifica su PAC**, recalcula firmas | más sigiloso: hay AS_REQ/TGS_REQ legítimo |
| **Sapphire ticket** | se reemplaza el PAC por el de un usuario potente obtenido vía **S4U2self + U2U** | aún más sigiloso: todo parece legítimo |

```bash
# Diamond / Sapphire con Impacket (requiere la clave del krbtgt o del servicio)
ticketer.py -request -domain <DOM> -user <USER> -password '<PASS>' \
            -nthash <KRBTGT_NTHASH> -aesKey <AES> ...

# Sapphire: usar -impersonate (obtiene el PAC del objetivo vía S4U2self+U2U)
ticketer.py -impersonate Administrator -domain <DOM> -user <USER> ...
```

## 2. Bronze Bit — CVE-2020-17049

S4U2proxy exige un tique de evidencia con el flag **`forwardable`**. Si falta (usuario en
*Protected Users*, cuenta *sensitive for delegation*, o KCD **Kerberos only sin protocol
transition**), no se puede delegar. Bronze Bit permite **editar el tique y poner el flag**.

```bash
getST.py -force-forwardable -spn "$Target_SPN" -impersonate Administrator \
         -dc-ip <DC_IP> '<DOM>/<SERVICE_ACCOUNT>:<PASS>'
```

> Encaja con la sección de delegación restringida de `05-active-directory.md`.

## 3. UnPAC the hash

Al obtener un TGT por **PKINIT** (autenticación con certificado), el KDC incluye en el PAC un
`PAC_CREDENTIAL_INFO` con las **claves NTLM** del usuario. Se recuperan con un **TGS-REQ vía
U2U + S4U2self**.

```bash
# 1) TGT por PKINIT
gettgtpkinit.py -cert-pfx <cert>.pfx <DOM>/<USER> <USER>.ccache
# 2) Recuperar el hash NT con el TGT + la session key
getnthash.py -key <AS_REP_KEY> <DOM>/<USER>
```

Muy útil tras **Shadow Credentials** o **Golden Certificate**: convertir un certificado en el
**hash NT** (para Pass-the-Hash). `certipy-ad auth` ya hace el atajo y devuelve el hash.

## 4. Dollar ticket y sAMAccountName spoofing

Ambos explotan la ambigüedad del **`$` final** de las cuentas de máquina.

- **Dollar ticket**: LPE en **sistemas Linux unidos al dominio** (SSH como root) por confusión
  de nombre; más simple, no escala a DA directamente.
- **sAMAccountName spoofing (noPac, CVE-2021-42278 + CVE-2021-42287)**: con `MachineAccountQuota > 0`
  se crea una cuenta de equipo, se renombra al nombre de un DC (sin `$`), se pide un TGT y se
  abusa de S4U2self para hacerse pasar por `Administrator` → DA.

```bash
# noPac / sam-the-admin
python3 noPac.py <DOM>/<USER>:<PASS> -dc-ip <DC_IP> --impersonate Administrator -use-ldap
```

## 5. Timeroasting

Abusa de la **extensión NTP de Microsoft**: el DC responde con un MAC calculado con la
contraseña de la cuenta de equipo/trust. Enviando peticiones con distintos **RID** se obtienen
hashes *password-equivalent* de cuentas de equipo con contraseñas débiles.

- **No requiere credenciales** (inicial access).
- Devuelve **RIDs**, no nombres → mapear con SMB null session / correlación.
- Crackear con hashcat/John.

```bash
# Herramienta Timeroast (o timeroast.py)
python3 timeroast.py <DC_IP> | tee timeroast.txt
hashcat -m 31300 timeroast.txt /usr/share/wordlists/rockyou.txt   # verificar modo
```

## 6. Pass-the-Certificate (Schannel)

Cuando el DC **no soporta PKINIT** (error `KDC_ERR_PADATA_TYPE_NOSUPP`), un certificado sigue
sirviendo para autenticar por **Schannel (TLS)**, por ejemplo contra **LDAPS**.

```bash
# PassTheCert (Python) o Certipy contra LDAP/S
certipy-ad auth -pfx <cert>.pfx -dc-ip <DC_IP> -ldap-shell
PassTheCert.py ...
```

## 7. SPN-jacking

Una KCD tiene en `msDS-AllowedToDelegateTo` una lista de SPNs. Si podés **mover un SPN** de su
objeto original a uno que controlás (o sobre el que tenés `WriteSPN`/`GenericWrite`), podés
abusan la delegación para comprometer el servicio listado.

> Requisito: `GenericAll`/`GenericWrite`/`WriteProperty` sobre el atributo `servicePrincipalName`.
> Idea original de Elad Shamir.

---

## 8. Coerción/relay adicionales

| Vector | Qué es |
| --- | --- |
| **DHCPv6 spoofing** | responder DHCPv6 + DNS spoofing para interceptar (alternativa a mitm6) |
| **WSUS / PushSubscription** | abusar de suscripciones para que un cliente descargue/invoque algo |
| **WebClient/WebDAV** | forzar autenticación HTTP con rutas `\\host@port\` |
| **MS-DHCP/Ms-Dfsnm/Fsrvp** | coerciones vistas en `cheatsheets/rpc-coercion.md` |

## 9. Exchange (más allá de OSCP)

| Vulnerabilidad | CVE(s) | Efecto |
| --- | --- | --- |
| **ProxyLogon** | CVE-2021-26855 (+26857/26858/27065) | RCE pre-auth en Exchange |
| **ProxyShell** | CVE-2021-34473 / 34523 / 31207 | RCE autenticada |
| **PrivExchange** | — | NTLM relay a LDAP/ADCS desde Exchange (`PushSubscription` → auth) |

## 10. SCCM / MECM (más allá de OSCP)

| Ataque | Idea |
| --- | --- |
| **Enumeración** | descubrir sitios, DP, MP, clientes (`sccmhunter`, `SharpSCCM`) |
| **Client Push Coercion** | forzar al servidor SCCM a autenticarse (relay → admin) |
| **Credential harvesting** | secretos en políticas de despliegue/NAA |
| **Site takeover** | comprometer el site server → control del entorno |
| **Hierarchy takeover** | tomar el CAS/site primario → control de todos los clientes |

Herramientas: `sccmhunter.py`, `SharpSCCM.exe`.

---

## Cómo usar esta chuleta

- **OSCP**: leéla solo para reconocer. El plan del examen está en `05-active-directory.md`.
- **Practice labs / CTF**: usala como índice; cada técnica enlaza con su fuente original.
- Si una técnica no te la podés explicar, no la ejecutes a ciegas: un tique forjado mal
  construido o un `krbtgt` tocado puede romper el dominio.
