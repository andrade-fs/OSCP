# WADComs: PwshADmodule-DelegationAttack-Enum

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[WADComs|Índice WADComs]]

> Fuente: [https://wadcoms.github.io/](https://wadcoms.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

WADComs — comandos para Active Directory, ordenados por lo que TENES.

**Lo que tenés:** `PowerShell`

**Sistema:** `Windows`

## Descripción

Having imported the pwsh AD module referenced in the project, we can begin to use it to enumerate for potential points of exploit
one of the prime being kerberos delegation attacks. The following 4 line commands will enumerate the entire AD forest for RBCD, Constrained and Unconstrained delegation attacks.
Note that we will also factor in protocol trainsiton as those change the attack vector slightly. See references below

## Comando

```bash
# 1. Unconstrained (turned on for all Domain controllers by default)
(Get-ADForest).Domains | % { Get-ADComputer -Filter {TrustedForDelegation -eq $true} -Server $_ | select Name,DNSHostName; Get-ADUser -Filter {TrustedForDelegation -eq $true} -Server $_ | select Name,SamAccountName }


# 2. Constrained (with protocol transition check)
(Get-ADForest).Domains | % { Get-ADComputer -Filter {msDS-AllowedToDelegateTo -like "*"} -Properties msDS-AllowedToDelegateTo,TrustedToAuthForDelegation -Server $_ | select Name,TrustedToAuthForDelegation,msDS-AllowedToDelegateTo; Get-ADUser -Filter {msDS-AllowedToDelegateTo -like "*"} -Properties msDS-AllowedToDelegateTo,TrustedToAuthForDelegation -Server $_ | select Name,TrustedToAuthForDelegation,msDS-AllowedToDelegateTo }

# 3. RBCD (which object is already configured)
(Get-ADForest).Domains | % { Get-ADComputer -Filter * -Properties msDS-AllowedToActOnBehalfOfOtherIdentity -Server $_ | ? {$_."msDS-AllowedToActOnBehalfOfOtherIdentity"} | select Name,DNSHostName }

# 4. RBCD (which object can configure it - write access)
(Get-ADForest).Domains | % { Get-ADComputer -Filter * -Properties nTSecurityDescriptor -Server $_ | ? {$_.nTSecurityDescriptor.Access | ? {$_.ActiveDirectoryRights -match "GenericWrite|WriteProperty" -and $_.IdentityReference -notmatch "SYSTEM|Domain Admins"}} | select Name }
```

## Referencias

- https://redfoxsec.com/blog/attacking-kerberos-delegation/
- https://shenaniganslabs.io/2019/01/28/Wagging-the-Dog.html
- https://dirkjanm.io/krbrelayx-unconstrained-delegation-abuse-toolkit/
- https://github.com/samratashok/ADModule
