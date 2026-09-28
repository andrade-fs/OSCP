# 🔑 AD — credenciales y loot (global)

> **El AD es un set encadenado**: lo que sacás de una máquina sirve en otra.
> Volcá aquí **todo** lo reutilizable y probalo contra **todas** las máquinas.
> Credenciales específicas de cada host: en [[ad-miembro-1]], [[ad-miembro-2]], [[ad-dc]].

[[00-dashboard|Panel]] · [[05-active-directory|AD (guía)]] · [[AD-walkthrough|Walkthrough AD]]

---

## 0. Credenciales iniciales (las que te dan)

| Usuario | Contraseña | Dominio | Notas |
| --- | --- | --- | --- |
| | | | *assumed breach* |

**Dominio:** `<dominio.local>` · **REALM:** `<DOMINIO.LOCAL>` · **DC IP:** `<DC_IP>`

```bash
export DOMAIN=''; export REALM=''; export DC_IP=''; export DC_HOST="dc.$DOMAIN"
echo "$DC_IP  $DOMAIN $DC_HOST" | sudo tee -a /etc/hosts
sudo ntpdate "$DC_IP"
```

---

## 1. Usuarios y contraseñas

| Usuario | Contraseña | De dónde salió | Probado en |
| --- | --- | --- | --- |
| | | | |

## 2. Hashes NTLM

| Usuario | Hash | De dónde salió | PtH probado en |
| --- | --- | --- | --- |
| | | | |

## 3. Tiques / ccache

| Usuario | Fichero | Tipo | Notas |
| --- | --- | --- | --- |
| | | | |

---

## 4. Matriz de acceso (usuario × máquina)

> Marcá dónde tenés admin local / sesión. `A` = admin local, `S` = sesión, `–` = nada.

| Usuario | [[ad-miembro-1]] | [[ad-miembro-2]] | [[ad-dc]] |
| --- | --- | --- | --- |
| | | | |

---

## 5. Grupos y ACLs encontrados

| Objeto | Derecho | Sobre | Cómo explotarlo |
| --- | --- | --- | --- |
| | | | |

> BloodHound: marcá tu usuario como **Owned** y buscá `Shortest Paths from Owned Principals`.

---

## 6. Notas del dominio

- DC / CA / otros hosts:
- Delegación / GPOs:
- SPNs / kerberoastables:
- Cuentas sin preauth (AS-REP):

---

## 7. Checklist AD

- [ ] `/etc/hosts` + DNS + reloj OK
- [ ] BloodHound recolectado (`-c all`) e importado
- [ ] Owned marcado y camino más corto identificado
- [ ] Kerberoast + AS-REP + spraying probados
- [ ] Creds iniciales probadas en **todos** los hosts
- [ ] No tocado el `krbtgt` (no cambiarlo nunca)
- [ ] ACLs/SPNs modificados → **restaurados**
