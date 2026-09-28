# Chuleta — ADCS: mapa completo de ESC

> Fuente: [The Hacker Recipes — ADCS](https://www.thehacker.recipes/ad/movement/adcs) y
> `labs.itresit.es` / material de SpecterOps.
> El vault ya tiene notas de **ESC1, ESC2, ESC3, ESC4, ESC6, ESC7, ESC8** y `golden-certificate.md`.
> Esta chuleta cubre **todo el mapa** y desarrolla los que faltaban.
>
> **Versión**: `certipy-ad` v5.1.0. La sintaxis NO es la de v4. Ver `cheatsheets/certipy.md`.

---

## Enumerar primero

```bash
certipy-ad find -u '<USER>@<dominio.local>' -p '<PASS>' -dc-ip <DC_IP> -vulnerable -stdout
```

Si hay una CA, revisá ADCS **temprano**: suele ser el camino más corto a Domain Admin.

---

## Mapa de ESC

| ESC | Vulnerabilidad | Requisito del atacante |
| --- | --- | --- |
| **ESC1** | Plantilla con `ENROLLEE_SUPPLIES_SUBJECT` + auth de cliente | poder enrolar |
| **ESC2** | EKU `Any Purpose` o sin EKU | poder enrolar |
| **ESC3** | Plantilla de *Enrollment Agent* | poder enrolar agente |
| **ESC4** | Permisos de escritura sobre la plantilla | `WriteDacl`/`GenericWrite` en la plantilla |
| **ESC5** | Permisos de escritura sobre **objetos PKI / CA** | control de objetos de ADCS |
| **ESC6** | `EDITF_ATTRIBUTESUBJECTALTNAME2` en la CA | poder enrolar |
| **ESC7** | CA Officer (`ManageCA`/`ManageCertificates`) | rol de oficial de CA |
| **ESC8** | Relay NTLM al endpoint **HTTP** de enrollment | coerción + relay |
| **ESC9** | Plantilla con `CT_FLAG_NO_SECURITY_EXTENSION` | cuenta con control + mapping débil |
| **ESC10** | Mapping débil (`StrongCertificateBindingEnforcement=0`) | control de una cuenta |
| **ESC11** | Relay NTLM al endpoint **RPC** (ICertPassage) sin cifrado | coerción + relay |
| **ESC12** | Acceso a la shell de la CA → robar su clave privada | admin en el host CA |
| **ESC13** | Plantilla con *issuance policy* OID ligada a un grupo | poder enrolar |
| **ESC14** | Mapping explícito débil (`altSecurityIdentities`) | escritura sobre el atributo |
| **ESC15** | `EKUwu` — inyección de EKU en plantillas v1 | poder enrolar |
| **Certifried** | CVE-2022-26923: `dNSHostName` de cuenta de equipo | crear cuenta de equipo |

---

## ESC5 — escribir sobre objetos PKI

Si controlás objetos de ADCS (plantillas, el objeto de la CA, contenedores
`CN=Public Key Services`, `NTAuthCertificates`, etc.), podés convertir eso en
compromiso total de la CA. Muchas veces aparece como `GenericAll`/`GenericWrite`
sobre el objeto de la CA en BloodHound.

**Efecto**: modificar la CA o sus ACLs para forjar certificados. Combinable con ESC7.

## ESC7 — CA Officer

Si sos miembro de `ManageCA` o `ManageCertificates` (oficial de la CA) podés
**habilitar** la emisión y conceder solicitudes pendientes.

```bash
# Con certipy (v5): gestionar la CA
certipy-ad ca -u '<USER>@<dominio.local>' -p '<PASS>' -dc-ip <DC_IP> -ca '<CA>' -add-officer '<USER>'
```

## ESC9 / ESC10 — Certificate Mapping

Un certificado normalmente se mapea a una cuenta por su **SID** (seguridad fuerte). Con
mapping débil, Windows puede mapear por **UPN**.

- **ESC9**: la plantilla tiene `CT_FLAG_NO_SECURITY_EXTENSION` (no incluye el SID).
- **ESC10**: el DC tiene `StrongCertificateBindingEnforcement=0` (mapping por UPN).

**Ataque**: pedís un certificado para una plantilla vulnerable, cambiás el UPN del objetivo
a otra cuenta controlada o viceversa, y el DC mapea al usuario equivocado → suplantación.

## ESC11 — relay al RPC de la CA

Como ESC8 pero contra la interfaz **ICertPassage** (RPC) sin cifrado, cuando el enrollment
HTTP no está disponible. Requiere coerción + relay.

## ESC12 — clave privada de la CA

Con acceso administrativo al **host de la CA**, robás su clave privada y forjás certificados
para cualquier usuario. Es equivalente al **Golden Certificate**
(`certipy-ad forge -ca-pfx <ca>.pfx ...`).

## ESC13 — issuance policy OID

Plantilla con una *issuance policy* ligada a un grupo. Al enrolar, obtenés un certificado que
implica pertenencia a ese grupo, dándote sus privilegios.

## ESC14 — altSecurityIdentities

Si podés escribir el atributo `altSecurityIdentities` de un usuario, podés mapear un
certificado tuyo a esa cuenta (mapping explícito).

## ESC15 (EKUwu) — CVE-2024-49019

Inyección de EKU / Application Policies en plantillas v1. El cliente puede incluir su propio
EKU con la plantilla v1, obteniendo un certificado usable para autenticación.

---

## Certifried — CVE-2022-26923

Abusa del atributo **`dNSHostName`** de una **cuenta de equipo** que el atacante puede
modificar (MachineAccountQuota). Se cambia el `dNSHostName` por el de un DC, se pide un
certificado para esa "máquina" y el compromiso apunta al DC.

```bash
# Requiere poder crear/controlar una cuenta de equipo (MachineAccountQuota > 0)
# Ver addcomputer + certipy req sobre la plantilla Machine
```

---

## Cadenas típicas

```text
ESC1  ─► req -upn administrator + auth ─────────────► hash NT del Administrator
ESC4  ─► modificar plantilla → explotar como ESC1 → RESTAURAR
ESC6  ─► req con SAN arbitrario ────────────────────► suplantación
ESC7  ─► habilitar emisión / aprobar solicitud ─────► certificado
ESC8  ─► relay + coerción ──────────────────────────► .pfx del DC → hash → DCSync
ESC11 ─► relay RPC (igual que ESC8 pero por ICertPassage)
───────► Golden Certificate (ESC12 / CA comprometida) → sobrevive al cambio de krbtgt
```

---

## Reglas de oro (para no romper el entorno del examen)

1. **BACKUP antes de modificar** una plantilla o ACL:
   `certipy-ad template ... -save-configuration original.json`.
2. **RESTAURAR** al terminar: `-write-configuration original.json`.
3. **No cambiar contraseñas** si podés evitar la vía destructiva (preferí Shadow Credentials).
4. Si `req` falla por resolución de nombre, agregá la CA y el DC a `/etc/hosts` y pasá `-ns`.
5. Anotá cada cambio para poder revertirlo: el reporte y el entorno lo agradecen.
