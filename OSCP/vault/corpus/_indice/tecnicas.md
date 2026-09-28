# Indice de tecnicas

Para cada tecnica, las maquinas donde aparece y cuantas veces.

Para ver el **contexto** de una tecnica:

```bash
python3 _sistema/herramientas/buscar.py kerberoasting -v
python3 _sistema/herramientas/buscar.py kerberoasting -v --oscp
```

---

## Ataques de credenciales AD

### kerberoasting _(tambien: kerberoast)_

33 maquinas.

[[htb-sherlock-campfire-1]] (32), [[htb-interactive]] (22), [[htb-tombwatcher]] (18), [[htb-rebound]] (16), [[htb-vintage]] (16), [[htb-sizzle]] (13), [[htb-mirage]] (11), [[htb-active]] (10), [[htb-breach]] (9), [[htb-administrator]] (7), [[htb-scrambled-win]] (7), [[htb-search]] (6), [[htb-voleur]] (6), [[htb-blazorized]] (5), [[htb-delegate]] (5), [[htb-object]] (5), [[htb-pirate]] (5), [[htb-blackfield]] (3), [[htb-intelligence]] (3), [[htb-absolute]] (2), [[htb-forest]] (2), [[htb-lustroustwo]] (2), [[htb-sherlock-campfire-2]] (2), [[htb-certified]] (1), [[htb-escape]] (1), [[htb-fluffy]] (1), [[htb-hospital]] (1), [[htb-jab]] (1), [[htb-pivotapi]] (1), [[htb-puppy]] (1), [[htb-sauna]] (1), [[htb-scrambled-linux]] (1), [[htb-scrambled]] (1)

### asreproast _(tambien: as-rep roast, asrep roast, as-rep roasting)_

11 maquinas.

[[htb-sauna]] (7), [[htb-forest]] (6), [[htb-multimaster]] (5), [[htb-sherlock-campfire-2]] (5), [[htb-bruno]] (3), [[htb-pivotapi]] (3), [[htb-active]] (2), [[htb-blackfield]] (1), [[htb-intelligence]] (1), [[htb-jab]] (1), [[htb-rebound]] (1)

### password spraying _(tambien: passwordspray)_

7 maquinas.

[[htb-apt]] (5), [[htb-phantom]] (2), [[htb-sekhmet]] (2), [[htb-darkcorp]] (1), [[htb-lustroustwo]] (1), [[htb-monteverde]] (1), [[htb-resolute]] (1)

### pass the hash _(tambien: pass-the-hash, pth)_

11 maquinas.

[[htb-blurry]] (32), [[htb-interactive]] (5), [[htb-conversor]] (3), [[htb-apt]] (2), [[htb-silo]] (2), [[htb-ypuffy]] (2), [[htb-flight]] (1), [[htb-jeeves]] (1), [[htb-nanocorp]] (1), [[htb-pivotapi-more]] (1), [[htb-sizzle]] (1)

### pass the ticket _(tambien: pass-the-ticket, ptt)_

3 maquinas.

[[htb-scrambled-win]] (3), [[htb-ghost]] (2), [[htb-support]] (1)

### dcsync

22 maquinas.

[[htb-interactive]] (21), [[htb-forest]] (13), [[htb-ghost]] (6), [[htb-sauna]] (6), [[htb-blazorized]] (4), [[htb-pivotapi-more]] (4), [[htb-scepter]] (4), [[htb-sizzle]] (4), [[htb-delegate]] (3), [[htb-hathor]] (3), [[htb-mist]] (3), [[htb-vintage]] (3), [[htb-administrator]] (2), [[htb-flight]] (2), [[htb-mirage]] (2), [[htb-rustykey]] (2), [[htb-darkcorp]] (1), [[htb-phantom]] (1), [[htb-pirate]] (1), [[htb-retrotwo]] (1), [[htb-signed]] (1), [[htb-university]] (1)

### golden ticket

5 maquinas.

[[htb-ghost]] (8), [[htb-mantis]] (2), [[htb-breach]] (1), [[htb-darkzero]] (1), [[htb-signed]] (1)

### silver ticket

9 maquinas.

[[htb-escape]] (8), [[htb-scrambled-win]] (7), [[htb-signed]] (7), [[htb-breach]] (5), [[htb-scrambled-linux]] (5), [[htb-sendai]] (4), [[htb-darkcorp]] (3), [[htb-authority]] (1), [[htb-scrambled]] (1)

### ntlm relay _(tambien: ntlmrelay, relay ntlm)_

16 maquinas.

[[htb-ghostlink]] (29), [[htb-apt]] (15), [[htb-pirate]] (15), [[htb-interactive]] (11), [[htb-signed]] (7), [[htb-university]] (7), [[htb-sherlock-reaper]] (5), [[htb-darkzero]] (4), [[htb-mist]] (4), [[htb-darkcorp]] (3), [[htb-vulncicada]] (3), [[htb-rebound]] (2), [[htb-nanocorp]] (1), [[htb-scrambled-linux]] (1), [[htb-scrambled-win]] (1), [[htb-shibuya]] (1)

### responder

41 maquinas.

[[htb-interactive]] (27), [[htb-mailing]] (15), [[htb-ghost]] (13), [[htb-apt]] (11), [[htb-querier]] (11), [[htb-signed]] (11), [[htb-darkzero]] (10), [[htb-lustroustwo]] (10), [[htb-ghostlink]] (8), [[htb-darkcorp]] (6), [[htb-overwatch]] (6), [[htb-sherlock-nubilum-1]] (6), [[htb-flight]] (5), [[htb-forwardslash]] (5), [[htb-giddy]] (5), [[htb-helpline]] (5), [[htb-intelligence]] (5), [[htb-media]] (5), [[htb-pirate]] (5), [[htb-sizzle]] (5), [[htb-fluffy]] (4), [[htb-fries]] (4), [[htb-re]] (4), [[htb-streamio]] (4), [[htb-breach]] (3), [[htb-driver]] (3), [[htb-escape]] (3), [[htb-reel2]] (3), [[htb-anubis]] (2), [[htb-arkham]] (2), [[htb-giveback]] (2), [[htb-nanocorp]] (2), [[htb-sherlock-noxious]] (2), [[htb-authority]] (1), [[htb-bankrobber]] (1), [[htb-ethereal-shell]] (1), [[htb-ethereal]] (1), [[htb-kryptos]] (1), [[htb-mist]] (1), [[htb-redelegate]] (1), [[htb-sherlock-tracer]] (1)

### responder poisoning _(tambien: llmnr)_

10 maquinas.

[[htb-sherlock-noxious]] (19), [[htb-sherlock-reaper]] (5), [[htb-mailing]] (3), [[htb-forwardslash]] (2), [[htb-ghost]] (2), [[htb-giddy]] (2), [[htb-querier]] (2), [[htb-darkzero]] (1), [[htb-fries]] (1), [[htb-joker]] (1)


## Active Directory — estructura y permisos

### bloodhound _(tambien: sharphound)_

62 maquinas.

[[htb-interactive]] (108), [[htb-ghost]] (64), [[htb-mist]] (33), [[htb-rebound]] (27), [[htb-sherlock-logjammer]] (27), [[htb-object]] (24), [[htb-reel]] (24), [[htb-blazorized]] (21), [[htb-certified]] (18), [[htb-administrator]] (16), [[htb-pivotapi]] (16), [[htb-tombwatcher]] (16), [[htb-puppy]] (14), [[htb-shibuya]] (14), [[htb-certificate]] (13), [[htb-haze]] (13), [[htb-sauna]] (13), [[htb-absolute]] (12), [[htb-fluffy]] (12), [[htb-university]] (12), [[htb-eighteen]] (11), [[htb-axlle]] (10), [[htb-infiltrator]] (10), [[htb-multimaster]] (10), [[htb-search]] (10), [[htb-vintage]] (10), [[htb-blackfield]] (9), [[htb-lustroustwo]] (9), [[htb-mirage]] (9), [[htb-outdated]] (9), [[htb-support]] (9), [[htb-intelligence]] (8), [[htb-logging]] (8), [[htb-pirate]] (8), [[htb-rustykey]] (8), [[htb-scepter]] (8), [[htb-darkzero]] (7), [[htb-forest]] (7), [[htb-sendai]] (7), [[htb-babytwo]] (6), [[htb-escapetwo]] (6), [[htb-freelancer]] (6), [[htb-jab]] (6), [[htb-voleur]] (6), [[htb-coder]] (5), [[htb-fries]] (5), [[htb-nanocorp]] (5), [[htb-phantom]] (5), [[htb-retrotwo]] (5), [[htb-sizzle]] (5), [[htb-streamio]] (5), [[htb-sweep]] (5), [[htb-breach]] (4), [[htb-darkcorp]] (4), [[htb-delegate]] (4), [[htb-redelegate]] (3), [[htb-ghostlink]] (2), [[htb-cypher]] (1), [[htb-escape]] (1), [[htb-manager]] (1)

_(y 2 mas)_

### ldap

141 maquinas.

[[htb-baby]] (732), [[htb-pirate]] (139), [[htb-rebound]] (120), [[htb-lightweight]] (105), [[htb-ghost]] (84), [[htb-absolute]] (81), [[htb-ctf]] (73), [[htb-scepter]] (73), [[htb-vintage]] (73), [[htb-darkzero]] (68), [[htb-haze]] (67), [[htb-fries]] (65), [[htb-interactive]] (65), [[htb-logging]] (64), [[htb-retrotwo]] (63), [[htb-authority]] (61), [[htb-tombwatcher]] (60), [[htb-mirage]] (54), [[htb-response]] (51), [[htb-voleur]] (50), [[htb-travel]] (49), [[htb-support]] (48), [[htb-sendai]] (45), [[htb-university]] (44), [[htb-mist]] (41), [[htb-redelegate]] (41), [[htb-darkcorp]] (40), [[htb-phantom]] (40), [[htb-delegate]] (39), [[htb-scrambled-linux]] (38), [[htb-search]] (38), [[htb-manager]] (37), [[htb-rustykey]] (37), [[htb-logforge]] (36), [[htb-sweep]] (36), [[htb-ghostlink]] (33), [[htb-cicada]] (32), [[htb-infiltrator]] (32), [[htb-breach]] (30), [[htb-corporate]] (29), [[htb-blackfield]] (26), [[htb-bruno]] (26), [[htb-analysis]] (24), [[htb-intelligence]] (24), [[htb-certificate]] (23), [[htb-cascade]] (22), [[chuleta-smb-enum]] (22), [[htb-fluffy]] (21), [[htb-nanocorp]] (21), [[htb-puppy]] (21), [[htb-lustroustwo]] (20), [[htb-outdated]] (20), [[htb-overwatch]] (20), [[htb-shibuya]] (20), [[htb-jab]] (19), [[htb-sekhmet]] (19), [[htb-sizzle]] (18), [[htb-fulcrum]] (17), [[htb-pikaboo]] (17), [[htb-babytwo]] (16)

_(y 81 mas)_

### kerberos

128 maquinas.

[[htb-rebound]] (36), [[htb-tentacle]] (35), [[htb-interactive]] (34), [[htb-absolute]] (24), [[htb-ghost]] (18), [[htb-lustroustwo]] (16), [[htb-vintage]] (16), [[htb-hathor]] (15), [[htb-infiltrator]] (15), [[htb-logging]] (14), [[htb-sekhmet]] (14), [[htb-shibuya]] (14), [[htb-scrambled-linux]] (13), [[htb-mirage]] (12), [[htb-scepter]] (12), [[htb-certificate]] (11), [[htb-flight]] (11), [[htb-rustykey]] (11), [[htb-anubis]] (10), [[htb-bruno]] (10), [[htb-darkzero]] (10), [[htb-intelligence]] (10), [[htb-office]] (10), [[htb-pirate]] (10), [[htb-retro]] (10), [[htb-voleur]] (10), [[htb-vulncicada]] (10), [[htb-apt]] (9), [[htb-mantis]] (9), [[htb-mist]] (9), [[htb-sauna]] (9), [[htb-thefrizz]] (9), [[htb-active]] (8), [[htb-administrator]] (8), [[htb-blazorized]] (8), [[htb-coder]] (8), [[htb-darkcorp]] (8), [[htb-escape]] (8), [[htb-jab]] (8), [[htb-timelapse]] (8), [[htb-manager]] (7), [[htb-sherlock-campfire-2]] (7), [[htb-support]] (7), [[htb-university]] (7), [[htb-analysis]] (6), [[htb-authority]] (6), [[htb-breach]] (6), [[htb-fluffy]] (6), [[htb-forest]] (6), [[htb-haze]] (6), [[htb-nanocorp]] (6), [[htb-sorcery]] (6), [[htb-baby]] (5), [[htb-blackfield]] (5), [[htb-cicada]] (5), [[htb-delegate]] (5), [[htb-fries]] (5), [[htb-ghostlink]] (5), [[htb-overwatch]] (5), [[htb-pivotapi]] (5)

_(y 68 mas)_

### delegacion sin restriccion _(tambien: unconstrained delegation)_

5 maquinas.

[[htb-delegate]] (8), [[htb-university]] (4), [[htb-redelegate]] (3), [[htb-pirate]] (1), [[htb-rebound]] (1)

### delegacion restringida _(tambien: constrained delegation)_

14 maquinas.

[[htb-rebound]] (8), [[htb-pirate]] (5), [[htb-redelegate]] (5), [[htb-delegate]] (3), [[htb-freelancer]] (2), [[htb-vintage]] (2), [[htb-authority]] (1), [[htb-bruno]] (1), [[htb-darkzero]] (1), [[htb-mirage]] (1), [[htb-mist]] (1), [[htb-phantom]] (1), [[htb-rustykey]] (1), [[htb-support]] (1)

### rbcd _(tambien: resource-based constrained delegation)_

15 maquinas.

[[htb-interactive]] (12), [[htb-freelancer]] (11), [[htb-rebound]] (7), [[htb-mirage]] (6), [[htb-phantom]] (6), [[htb-rustykey]] (6), [[htb-pirate]] (5), [[htb-bruno]] (4), [[htb-redelegate]] (3), [[htb-vintage]] (3), [[htb-mist]] (2), [[htb-university]] (2), [[htb-authority]] (1), [[htb-darkzero]] (1), [[htb-support]] (1)

### shadow credentials _(tambien: msds-keycredentiallink, key credential)_

12 maquinas.

[[htb-certified]] (17), [[htb-haze]] (14), [[htb-escapetwo]] (13), [[htb-mist]] (13), [[htb-absolute]] (10), [[htb-outdated]] (10), [[htb-darkcorp]] (8), [[htb-fluffy]] (8), [[htb-infiltrator]] (8), [[htb-rebound]] (8), [[htb-tombwatcher]] (8), [[htb-logging]] (1)

### genericall

24 maquinas.

[[htb-interactive]] (8), [[htb-haze]] (7), [[htb-tombwatcher]] (7), [[htb-infiltrator]] (6), [[htb-certified]] (4), [[htb-rebound]] (4), [[htb-scepter]] (4), [[htb-signed]] (4), [[htb-forest]] (3), [[htb-support]] (3), [[htb-escapetwo]] (2), [[htb-puppy]] (2), [[htb-redelegate]] (2), [[htb-administrator]] (1), [[htb-babytwo]] (1), [[htb-certificate]] (1), [[htb-darkzero]] (1), [[htb-fluffy]] (1), [[htb-search]] (1), [[htb-sendai]] (1), [[htb-sherlock-bumblebee]] (1), [[htb-sweep]] (1), [[htb-university]] (1), [[htb-vintage]] (1)

### genericwrite

16 maquinas.

[[htb-multimaster]] (17), [[htb-fluffy]] (7), [[htb-interactive]] (7), [[htb-control]] (6), [[htb-freelancer]] (6), [[htb-logging]] (6), [[htb-administrator]] (4), [[htb-object]] (4), [[htb-certified]] (2), [[htb-darkcorp]] (2), [[htb-delegate]] (2), [[htb-puppy]] (2), [[htb-vintage]] (2), [[htb-absolute]] (1), [[htb-retrotwo]] (1), [[htb-rustykey]] (1)

### writedacl

8 maquinas.

[[htb-mist]] (15), [[htb-forest]] (3), [[htb-reel]] (2), [[htb-interactive]] (2), [[htb-anubis]] (1), [[htb-babytwo]] (1), [[htb-escape]] (1), [[htb-haze]] (1)

### writeowner

15 maquinas.

[[htb-mist]] (15), [[htb-interactive]] (5), [[htb-reel]] (4), [[htb-certified]] (2), [[htb-escapetwo]] (2), [[htb-haze]] (2), [[htb-object]] (2), [[htb-querier]] (2), [[htb-tombwatcher]] (2), [[htb-anubis]] (1), [[htb-babytwo]] (1), [[htb-darkzero]] (1), [[htb-escape]] (1), [[htb-signed]] (1), [[htb-streamio]] (1)

### forcechangepassword

15 maquinas.

[[htb-interactive]] (9), [[htb-object]] (2), [[htb-rustykey]] (2), [[htb-tombwatcher]] (2), [[htb-administrator]] (1), [[htb-axlle]] (1), [[htb-blackfield]] (1), [[htb-infiltrator]] (1), [[htb-mirage]] (1), [[htb-nanocorp]] (1), [[htb-phantom]] (1), [[htb-pirate]] (1), [[htb-pivotapi]] (1), [[htb-redelegate]] (1), [[htb-scepter]] (1)

### addmember _(tambien: addself)_

6 maquinas.

[[htb-interactive]] (5), [[htb-rustykey]] (3), [[htb-certified]] (1), [[htb-infiltrator]] (1), [[htb-tombwatcher]] (1), [[htb-vintage]] (1)

### dnstool _(tambien: admindns, dnscmd)_

9 maquinas.

[[htb-interactive]] (9), [[htb-resolute]] (5), [[htb-ghost]] (3), [[htb-intelligence]] (3), [[htb-darkzero]] (2), [[htb-signed]] (2), [[htb-delegate]] (1), [[htb-mist]] (1), [[htb-pirate]] (1)

### machineaccountquota

21 maquinas.

[[htb-mist]] (6), [[htb-authority]] (5), [[htb-delegate]] (5), [[htb-haze]] (4), [[htb-bruno]] (3), [[htb-darkcorp]] (3), [[htb-pirate]] (3), [[htb-redelegate]] (3), [[htb-support]] (3), [[htb-vulncicada]] (3), [[htb-interactive]] (3), [[htb-phantom]] (2), [[htb-breach]] (1), [[htb-darkzero]] (1), [[htb-ghostlink]] (1), [[htb-retrotwo]] (1), [[htb-sendai]] (1), [[htb-sweep]] (1), [[htb-tombwatcher]] (1), [[htb-university]] (1), [[htb-voleur]] (1)

### gmsa _(tambien: group managed service account)_

17 maquinas.

[[htb-vintage]] (71), [[htb-pirate]] (52), [[htb-fries]] (39), [[htb-interactive]] (23), [[htb-haze]] (18), [[htb-university]] (14), [[htb-logging]] (13), [[htb-rebound]] (12), [[htb-search]] (11), [[htb-intelligence]] (7), [[htb-infiltrator]] (6), [[htb-sendai]] (5), [[htb-tombwatcher]] (5), [[htb-ghost]] (4), [[htb-mirage]] (4), [[htb-mist]] (3), [[htb-eighteen]] (1)

### laps

9 maquinas.

[[htb-pivotapi]] (18), [[htb-napper]] (17), [[htb-timelapse]] (16), [[htb-streamio]] (7), [[htb-interactive]] (5), [[htb-darkcorp]] (4), [[htb-authority]] (1), [[htb-darkzero]] (1), [[htb-mist]] (1)


## ADCS (certificate services)

### adcs

32 maquinas.

[[htb-interactive]] (30), [[htb-coder]] (23), [[chuleta-smb-enum]] (22), [[htb-tombwatcher]] (15), [[htb-ghostlink]] (14), [[htb-fluffy]] (12), [[htb-darkcorp]] (9), [[htb-authority]] (8), [[htb-escape]] (8), [[htb-darkzero]] (7), [[htb-infiltrator]] (7), [[htb-mist]] (7), [[htb-vulncicada]] (7), [[htb-certified]] (6), [[htb-fries]] (6), [[htb-certificate]] (4), [[htb-manager]] (4), [[htb-anubis]] (3), [[htb-escapetwo]] (3), [[htb-logging]] (3), [[htb-mirage]] (3), [[htb-sendai]] (3), [[htb-absolute]] (2), [[htb-pirate]] (2), [[htb-rebound]] (2), [[htb-retro]] (2), [[htb-shibuya]] (2), [[htb-administrator]] (1), [[htb-puppy]] (1), [[htb-rustykey]] (1), [[htb-vintage]] (1), [[htb-voleur]] (1)

### esc1

17 maquinas.

[[htb-interactive]] (22), [[htb-coder]] (12), [[htb-fries]] (11), [[htb-ghostlink]] (9), [[htb-logging]] (8), [[htb-mist]] (8), [[htb-fluffy]] (7), [[htb-mirage]] (7), [[htb-shibuya]] (7), [[htb-tombwatcher]] (7), [[htb-authority]] (6), [[htb-scepter]] (4), [[htb-sendai]] (4), [[htb-escapetwo]] (3), [[htb-retro]] (3), [[htb-infiltrator]] (2), [[htb-escape]] (1)

### esc2

4 maquinas.

[[htb-fluffy]] (4), [[htb-tombwatcher]] (3), [[htb-shibuya]] (2), [[htb-infiltrator]] (1)

### esc3

6 maquinas.

[[htb-certificate]] (4), [[htb-fluffy]] (4), [[htb-tombwatcher]] (4), [[htb-interactive]] (3), [[htb-shibuya]] (2), [[htb-infiltrator]] (1)

### esc4

5 maquinas.

[[htb-sendai]] (9), [[htb-infiltrator]] (7), [[htb-escapetwo]] (5), [[htb-interactive]] (4), [[htb-coder]] (2)

### esc6

2 maquinas.

[[htb-fries]] (23), [[htb-interactive]] (2)

### esc7

3 maquinas.

[[htb-fries]] (8), [[htb-manager]] (5), [[htb-interactive]] (3)

### esc8

4 maquinas.

[[htb-ghostlink]] (10), [[htb-vulncicada]] (8), [[htb-interactive]] (3), [[htb-shibuya]] (2)

### certipy

26 maquinas.

[[htb-fluffy]] (29), [[htb-interactive]] (28), [[htb-mist]] (27), [[htb-scepter]] (27), [[htb-fries]] (26), [[htb-escapetwo]] (25), [[htb-tombwatcher]] (24), [[htb-certified]] (22), [[htb-certificate]] (21), [[htb-coder]] (18), [[htb-infiltrator]] (18), [[htb-manager]] (18), [[htb-mirage]] (18), [[htb-shibuya]] (18), [[htb-vulncicada]] (18), [[htb-retro]] (17), [[htb-authority]] (14), [[htb-sendai]] (12), [[htb-escape]] (10), [[htb-ghostlink]] (10), [[htb-rebound]] (10), [[htb-absolute]] (8), [[htb-logging]] (7), [[htb-darkcorp]] (6), [[htb-darkzero]] (5), [[htb-haze]] (5)

### certificate template _(tambien: plantilla de certificado)_

27 maquinas.

[[htb-mist]] (20), [[htb-certified]] (15), [[htb-fluffy]] (14), [[htb-fries]] (14), [[htb-tombwatcher]] (11), [[htb-infiltrator]] (10), [[htb-anubis]] (7), [[htb-escapetwo]] (7), [[htb-ghostlink]] (7), [[htb-mirage]] (7), [[htb-sendai]] (7), [[htb-logging]] (6), [[htb-manager]] (6), [[htb-shibuya]] (6), [[htb-authority]] (5), [[htb-certificate]] (5), [[htb-coder]] (5), [[htb-rebound]] (5), [[htb-retro]] (5), [[htb-scepter]] (5), [[htb-vulncicada]] (5), [[htb-absolute]] (3), [[htb-darkzero]] (2), [[htb-escape]] (2), [[htb-haze]] (2), [[htb-darkcorp]] (1), [[htb-pirate]] (1)

### golden certificate

1 maquinas.

[[htb-certificate]] (2)


## Escalada en Windows

### seimpersonate _(tambien: seimpersonateprivilege)_

38 maquinas.

[[htb-darkzero]] (24), [[htb-signed]] (22), [[htb-interactive]] (21), [[htb-pivotapi]] (11), [[htb-media]] (9), [[htb-tally]] (9), [[htb-visual]] (9), [[htb-ghost]] (8), [[htb-mailing]] (8), [[htb-pivotapi-more]] (8), [[htb-breach]] (6), [[htb-job]] (6), [[htb-perspective]] (6), [[htb-sendai]] (6), [[htb-cereal]] (5), [[htb-scrambled-beyond-root]] (5), [[htb-worker]] (5), [[htb-acute]] (4), [[htb-arkham]] (4), [[htb-bounty]] (4), [[htb-fighter]] (4), [[htb-haze]] (4), [[htb-json]] (4), [[htb-querier]] (4), [[htb-silo]] (4), [[htb-apt]] (2), [[htb-conceal]] (2), [[htb-escape]] (2), [[htb-ethereal]] (2), [[htb-freelancer]] (2), [[htb-grandpa]] (2), [[htb-hackback]] (2), [[htb-lustroustwo]] (2), [[htb-napper]] (2), [[htb-pov]] (2), [[htb-proper]] (2), [[htb-rainbow]] (2), [[htb-vulnescape]] (2)

### seassignprimarytoken

20 maquinas.

[[htb-darkzero]] (4), [[htb-signed]] (3), [[htb-visual]] (2), [[htb-bounty]] (1), [[htb-breach]] (1), [[htb-conceal]] (1), [[htb-ghost]] (1), [[htb-grandpa]] (1), [[htb-json]] (1), [[htb-mailing]] (1), [[htb-media]] (1), [[htb-perspective]] (1), [[htb-pivotapi-more]] (1), [[htb-pivotapi]] (1), [[htb-proper]] (1), [[htb-scrambled-beyond-root]] (1), [[htb-sendai]] (1), [[htb-silo]] (1), [[htb-tally]] (1), [[htb-worker]] (1)

### sebackupprivilege _(tambien: backup operators)_

15 maquinas.

[[htb-blackfield]] (24), [[htb-cicada]] (11), [[htb-baby]] (8), [[htb-freelancer]] (8), [[htb-interactive]] (6), [[htb-multimaster]] (3), [[htb-return]] (3), [[htb-acute]] (2), [[htb-arkham]] (2), [[htb-mist]] (2), [[htb-darkzero]] (1), [[htb-napper]] (1), [[htb-pivotapi]] (1), [[htb-rainbow]] (1), [[htb-vulnescape]] (1)

### serestoreprivilege

13 maquinas.

[[htb-multimaster]] (3), [[htb-acute]] (2), [[htb-arkham]] (2), [[htb-cicada]] (2), [[htb-return]] (2), [[htb-interactive]] (2), [[htb-baby]] (1), [[htb-blackfield]] (1), [[htb-darkzero]] (1), [[htb-freelancer]] (1), [[htb-napper]] (1), [[htb-rainbow]] (1), [[htb-vulnescape]] (1)

### setakeownershipprivilege _(tambien: takedown)_

6 maquinas.

[[htb-acute]] (2), [[htb-arkham]] (2), [[htb-darkzero]] (1), [[htb-napper]] (1), [[htb-rainbow]] (1), [[htb-vulnescape]] (1)

### sedebugprivilege

8 maquinas.

[[htb-pov]] (8), [[htb-acute]] (2), [[htb-arkham]] (2), [[htb-darkzero]] (2), [[htb-interactive]] (2), [[htb-napper]] (1), [[htb-rainbow]] (1), [[htb-vulnescape]] (1)

### seloaddriverprivilege

8 maquinas.

[[htb-fuse]] (6), [[htb-acute]] (2), [[htb-arkham]] (2), [[htb-return]] (2), [[htb-darkzero]] (1), [[htb-napper]] (1), [[htb-rainbow]] (1), [[htb-vulnescape]] (1)

### potato _(tambien: juicy potato, juicy potato, roguepotato, sweetpotato, godpotato, efspotato)_

32 maquinas.

[[htb-interactive]] (28), [[htb-worker]] (21), [[htb-apt]] (14), [[htb-cereal]] (14), [[htb-ghost]] (12), [[htb-pivotapi-more]] (11), [[htb-darkzero]] (7), [[htb-haze]] (6), [[htb-tally]] (6), [[htb-breach]] (5), [[htb-fighter]] (5), [[htb-mailing]] (5), [[htb-signed]] (5), [[htb-visual]] (5), [[htb-job]] (4), [[htb-media]] (4), [[htb-scrambled-beyond-root]] (4), [[htb-sendai]] (4), [[htb-querier]] (3), [[htb-bounty]] (2), [[htb-perspective]] (2), [[htb-pirate]] (2), [[htb-pivotapi]] (2), [[htb-absolute]] (1), [[htb-conceal]] (1), [[htb-escape]] (1), [[htb-flight]] (1), [[htb-grandpa]] (1), [[htb-mirage]] (1), [[htb-proper]] (1), [[htb-rebound]] (1), [[htb-scanned]] (1)

### printspoofer

5 maquinas.

[[htb-pivotapi]] (6), [[htb-cereal]] (3), [[htb-tally]] (3), [[htb-interactive]] (3), [[htb-pivotapi-more]] (1)

### unquoted service path _(tambien: ruta sin comillas)_

1 maquinas.

[[htb-love]] (1)

### alwaysinstallelevated

2 maquinas.

[[htb-love]] (6), [[htb-interactive]] (2)

### dll hijack _(tambien: dll hijacking)_

2 maquinas.

[[htb-bruno]] (4), [[htb-querier]] (4)

### uac bypass

4 maquinas.

[[htb-arkham]] (7), [[htb-rainbow]] (2), [[htb-driver]] (1), [[htb-vulnescape]] (1)

### token impersonation

1 maquinas.

[[htb-object]] (2)

### amsi bypass

1 maquinas.

[[htb-multimaster]] (1)

### applocker bypass

5 maquinas.

[[htb-fighter]] (3), [[htb-ethereal-cor]] (1), [[htb-hackback]] (1), [[htb-hathor]] (1), [[htb-sekhmet]] (1)

### wmic

7 maquinas.

[[htb-hancliffe]] (2), [[htb-worker]] (2), [[htb-interactive]] (2), [[htb-hackback]] (1), [[htb-overwatch]] (1), [[htb-sherlock-i-like-to]] (1), [[htb-signed]] (1)

### scheduled task _(tambien: tarea programada)_

42 maquinas.

[[htb-darkcorp]] (10), [[htb-sherlock-logjammer]] (8), [[htb-bounty]] (5), [[htb-rabbit]] (5), [[htb-sherlock-einladen]] (5), [[htb-sniper-beyondroot]] (4), [[htb-monitorsfour]] (3), [[htb-napper]] (3), [[htb-tally]] (3), [[htb-visual]] (3), [[htb-bankrobber]] (2), [[htb-cascade]] (2), [[htb-forest]] (2), [[htb-fuse]] (2), [[htb-hackback]] (2), [[htb-hathor]] (2), [[htb-hospital]] (2), [[htb-investigation]] (2), [[htb-logging]] (2), [[htb-wifinetictwo]] (2), [[htb-arctic]] (1), [[htb-blackfield]] (1), [[htb-bruno]] (1), [[htb-darkzero]] (1), [[htb-derailed]] (1), [[htb-fighter]] (1), [[htb-helpline-kali]] (1), [[htb-helpline-win]] (1), [[htb-infiltrator]] (1), [[htb-mailing]] (1), [[htb-media]] (1), [[htb-nanocorp]] (1), [[htb-object]] (1), [[htb-permx]] (1), [[htb-proper]] (1), [[htb-sandworm]] (1), [[htb-schooled]] (1), [[htb-servmon]] (1), [[htb-sherlock-brutus]] (1), [[htb-sherlock-i-like-to]] (1), [[htb-sherlock-reaper]] (1), [[htb-signed]] (1)

### autorun

9 maquinas.

[[htb-chatterbox]] (5), [[htb-sherlock-nubilum-1]] (5), [[htb-breach]] (3), [[htb-flight]] (2), [[htb-freelancer]] (2), [[htb-sightless]] (2), [[htb-interactive]] (2), [[htb-derailed]] (1), [[htb-escapetwo]] (1)

### lsass

15 maquinas.

[[htb-blackfield]] (17), [[htb-infiltrator]] (17), [[htb-sherlock-tick-tock]] (4), [[htb-freelancer]] (3), [[htb-darkzero]] (2), [[htb-hancliffe]] (2), [[htb-sniper-beyondroot]] (2), [[htb-appsanity]] (1), [[htb-driver]] (1), [[htb-mirage]] (1), [[htb-re]] (1), [[htb-rebound]] (1), [[htb-remote]] (1), [[htb-sendai]] (1), [[htb-signed]] (1)

### sam dump _(tambien: dump sam, hives)_

14 maquinas.

[[htb-mist]] (4), [[htb-acute]] (3), [[htb-cicada]] (3), [[htb-outdated]] (3), [[htb-shibuya]] (3), [[htb-freelancer]] (2), [[htb-omni]] (2), [[htb-appsanity]] (1), [[htb-bastion]] (1), [[htb-ghostlink]] (1), [[htb-sherlock-i-like-to]] (1), [[htb-sherlock-pikaptcha]] (1), [[htb-silo]] (1), [[htb-voleur]] (1)

### procdump

3 maquinas.

[[htb-heist]] (6), [[htb-interactive]] (2), [[htb-blackfield]] (1)

### mimikatz

14 maquinas.

[[htb-helpline-kali]] (19), [[htb-office]] (17), [[htb-sauna]] (13), [[htb-ghost]] (10), [[htb-interactive]] (10), [[htb-blazorized]] (9), [[htb-freelancer]] (6), [[htb-sekhmet]] (6), [[htb-access]] (5), [[htb-re]] (5), [[htb-apt]] (4), [[htb-blackfield]] (2), [[htb-darkzero]] (1), [[htb-forest]] (1)

### rubeus

18 maquinas.

[[htb-sherlock-campfire-1]] (15), [[htb-interactive]] (15), [[htb-support]] (11), [[htb-darkzero]] (10), [[htb-anubis]] (8), [[htb-mist]] (8), [[htb-scrambled-win]] (8), [[htb-escape]] (5), [[htb-pivotapi-more]] (5), [[htb-flight]] (4), [[htb-university]] (4), [[htb-outdated]] (3), [[htb-sizzle]] (3), [[htb-absolute]] (2), [[htb-ghost]] (2), [[htb-logging]] (2), [[htb-eighteen]] (1), [[htb-rebound]] (1)

### sevendll _(tambien: printnightmare)_

3 maquinas.

[[htb-driver]] (5), [[htb-atom]] (3), [[htb-interactive]] (3)


## Escalada en Linux

### suid

84 maquinas.

[[htb-tartarsauce-part-2-backuperer-follow-up]] (28), [[htb-altered]] (14), [[htb-interactive]] (14), [[htb-pandora]] (13), [[htb-shrek]] (12), [[htb-bank]] (7), [[htb-haircut]] (7), [[htb-jail]] (6), [[htb-laboratory]] (6), [[htb-mango]] (5), [[htb-pterodactyl]] (5), [[htb-snapped]] (5), [[htb-wall]] (5), [[htb-flujab]] (4), [[htb-lame-more]] (4), [[htb-openkeys]] (4), [[htb-admirer]] (3), [[htb-chainsaw]] (3), [[htb-dynstr]] (3), [[htb-dyplesher]] (3), [[htb-fingerprint]] (3), [[htb-forwardslash]] (3), [[htb-magic]] (3), [[htb-secret]] (3), [[htb-smasher2]] (3), [[htb-backdoor]] (2), [[htb-carpediem]] (2), [[htb-ctf]] (2), [[htb-ellingson]] (2), [[htb-expressway]] (2), [[htb-ghoul]] (2), [[htb-goodgames]] (2), [[htb-jarvis]] (2), [[htb-lazy]] (2), [[htb-monitors]] (2), [[htb-obscurity]] (2), [[htb-october]] (2), [[htb-pit]] (2), [[htb-playertwo]] (2), [[htb-ropetwo]] (2), [[htb-scriptkiddie]] (2), [[htb-tabby]] (2), [[htb-unicode]] (2), [[htb-yummy]] (2), [[htb-zipper]] (2), [[htb-agile]] (1), [[htb-ambassador]] (1), [[htb-beep]] (1), [[htb-boardlight]] (1), [[htb-cache]] (1), [[htb-calamity]] (1), [[htb-chaos]] (1), [[htb-charon]] (1), [[htb-compromised]] (1), [[htb-crossfittwo]] (1), [[htb-earlyaccess]] (1), [[htb-editor]] (1), [[htb-enterprise]] (1), [[htb-faculty]] (1), [[htb-falafel]] (1)

_(y 24 mas)_

### sgid

11 maquinas.

[[htb-openkeys]] (10), [[htb-ctf]] (2), [[htb-pit]] (2), [[htb-yummy]] (2), [[htb-falafel]] (1), [[htb-fingerprint]] (1), [[htb-jail]] (1), [[htb-scanned]] (1), [[htb-scavenger]] (1), [[htb-shrek]] (1), [[htb-smasher2]] (1)

### capabilities _(tambien: getcap, setcap)_

67 maquinas.

[[htb-skyfall]] (34), [[htb-earlyaccess]] (16), [[htb-scanned]] (16), [[htb-waldo]] (12), [[htb-cap]] (10), [[htb-interactive]] (10), [[htb-jab]] (7), [[htb-chaos]] (6), [[htb-lightweight]] (6), [[htb-retired]] (5), [[htb-analytics]] (4), [[htb-formulax]] (4), [[htb-beep]] (3), [[htb-brainfuck]] (3), [[htb-carpediem]] (3), [[htb-cybermonday]] (3), [[htb-dyplesher]] (3), [[htb-faculty]] (3), [[htb-fulcrum]] (3), [[htb-gofer]] (3), [[htb-hospital]] (3), [[htb-mailing]] (3), [[htb-smasher2]] (3), [[htb-talkative]] (3), [[htb-wifinetic]] (3), [[htb-ambassador]] (2), [[htb-cctv]] (2), [[htb-cerberus]] (2), [[htb-editor]] (2), [[htb-hackback]] (2), [[htb-intentions]] (2), [[htb-rabbit]] (2), [[htb-snapped]] (2), [[htb-sneakymailer]] (2), [[htb-snoopy]] (2), [[htb-static]] (2), [[htb-wifinetictwo]] (2), [[htb-backendtwo]] (1), [[htb-broker]] (1), [[htb-conceal]] (1), [[htb-cypher]] (1), [[htb-darkzero]] (1), [[htb-devoops]] (1), [[htb-dropzone]] (1), [[htb-ethereal-cor]] (1), [[htb-forest]] (1), [[htb-ghostlink]] (1), [[htb-giveback]] (1), [[htb-kotarak]] (1), [[htb-magicgardens]] (1), [[htb-monitors]] (1), [[htb-monitorsfour]] (1), [[htb-nunchucks]] (1), [[htb-oz]] (1), [[htb-pikatwoo]] (1), [[htb-pressed]] (1), [[htb-pterodactyl]] (1), [[htb-signed]] (1), [[htb-silo]] (1), [[htb-soccer]] (1)

_(y 7 mas)_

### sudo _(tambien: sudoers)_

377 maquinas.

[[htb-expressway]] (97), [[htb-interactive]] (74), [[htb-dump]] (60), [[htb-sorcery]] (58), [[htb-joker]] (57), [[htb-permx]] (52), [[htb-manage]] (49), [[htb-previse]] (41), [[htb-intuition]] (35), [[htb-giveback]] (31), [[htb-airtouch]] (30), [[htb-mist]] (28), [[htb-frolic]] (27), [[htb-obscurity]] (27), [[htb-sherlock-brutus]] (27), [[htb-sunday]] (25), [[htb-admirer]] (23), [[htb-tentacle]] (23), [[htb-feline]] (22), [[htb-snoopy]] (22), [[htb-agile]] (21), [[htb-fries]] (20), [[htb-guardian]] (20), [[htb-barrier]] (19), [[htb-blunder]] (19), [[htb-ariekei]] (18), [[htb-blockblock]] (18), [[htb-dynstr]] (18), [[htb-mango]] (18), [[htb-formulax]] (17), [[htb-oz]] (17), [[htb-passage]] (17), [[htb-pterodactyl]] (17), [[htb-university]] (17), [[htb-variatype]] (17), [[htb-busqueda]] (16), [[htb-jewel]] (16), [[htb-node]] (16), [[htb-paper]] (16), [[htb-canape]] (15), [[htb-codetwo]] (15), [[htb-flustered]] (15), [[htb-forgotten]] (15), [[htb-imagery]] (15), [[htb-previous]] (15), [[htb-sandworm]] (15), [[htb-schooled]] (15), [[htb-whiterabbit]] (15), [[htb-backendtwo]] (14), [[htb-crossfittwo]] (14), [[htb-data]] (14), [[htb-jail]] (14), [[htb-nodeblog]] (14), [[htb-travel]] (14), [[htb-browsed]] (13), [[htb-clicker]] (13), [[htb-encoding]] (13), [[htb-outbound]] (13), [[htb-rainyday]] (13), [[htb-backfire]] (12)

_(y 317 mas)_

### gtfobins

34 maquinas.

[[htb-interactive]] (18), [[htb-knife]] (4), [[htb-mango]] (4), [[htb-meta]] (3), [[htb-nunchucks]] (3), [[htb-schooled]] (3), [[htb-academy]] (2), [[htb-cozyhosting]] (2), [[htb-jewel]] (2), [[htb-lame-more]] (2), [[htb-openadmin]] (2), [[htb-strutted]] (2), [[htb-swagshop]] (2), [[htb-awkward]] (1), [[htb-chaos]] (1), [[htb-conversor]] (1), [[htb-devvortex]] (1), [[htb-dump]] (1), [[htb-earlyaccess]] (1), [[htb-facts]] (1), [[htb-flujab]] (1), [[htb-jail]] (1), [[htb-jarvis]] (1), [[htb-joker]] (1), [[htb-luanne]] (1), [[htb-monitorstwo]] (1), [[htb-paper]] (1), [[htb-shoppy]] (1), [[htb-sunday]] (1), [[htb-traverxec]] (1), [[htb-unrested]] (1), [[htb-updown]] (1), [[htb-writer]] (1), [[htb-zero]] (1)

### cron

169 maquinas.

[[htb-cronos]] (59), [[htb-permx]] (43), [[htb-interactive]] (33), [[htb-caption]] (30), [[htb-planning]] (26), [[htb-yummy]] (25), [[htb-inception]] (23), [[htb-crossfit]] (22), [[htb-ellingson]] (22), [[htb-phoenix]] (22), [[htb-derailed]] (19), [[htb-reddish]] (18), [[htb-europa]] (17), [[htb-corporate]] (16), [[htb-nexus]] (15), [[htb-pikaboo]] (15), [[htb-crossfittwo]] (14), [[htb-race]] (14), [[htb-rope]] (14), [[htb-monitors]] (13), [[htb-sherlock-bumblebee]] (13), [[htb-topology]] (13), [[htb-traceback]] (13), [[htb-imagery]] (12), [[htb-registry]] (12), [[htb-shrek]] (12), [[htb-celestial]] (11), [[htb-kotarak]] (10), [[htb-sherlock-brutus]] (10), [[htb-zero]] (10), [[htb-fatty]] (9), [[htb-flujab]] (9), [[htb-writeup]] (9), [[htb-attended]] (8), [[htb-book]] (8), [[htb-interface]] (8), [[htb-lightweight]] (8), [[htb-meta]] (8), [[htb-ypuffy]] (8), [[htb-broscience]] (7), [[htb-carpediem]] (7), [[htb-carrier]] (7), [[htb-era]] (7), [[htb-ghoul]] (7), [[htb-inject]] (7), [[htb-retired]] (7), [[htb-sandworm]] (7), [[htb-sorcery]] (7), [[htb-wifinetictwo]] (7), [[htb-aragog]] (6), [[htb-conversor]] (6), [[htb-dyplesher]] (6), [[htb-health]] (6), [[htb-oz]] (6), [[htb-playertwo]] (6), [[htb-previous]] (6), [[htb-variatype]] (6), [[htb-friendzone]] (5), [[htb-jupiter]] (5), [[htb-mischief-more-root]] (5)

_(y 109 mas)_

### systemd

114 maquinas.

[[htb-caption]] (66), [[htb-devarea]] (32), [[htb-abducted]] (27), [[htb-tartarsauce-part-2-backuperer-follow-up]] (26), [[htb-gavel]] (23), [[htb-zipper]] (23), [[htb-clicker]] (22), [[htb-cobblestone]] (21), [[htb-nexus]] (21), [[htb-bookworm]] (20), [[htb-orion]] (18), [[htb-store]] (18), [[htb-strutted]] (18), [[htb-iclean]] (17), [[htb-snapped]] (17), [[htb-silentium]] (16), [[htb-ouija]] (15), [[htb-flujab]] (14), [[htb-inception]] (14), [[htb-talkative]] (13), [[htb-aragog]] (12), [[htb-book]] (12), [[htb-encoding]] (12), [[htb-wifinetictwo]] (12), [[htb-zero]] (12), [[htb-pilgrimage]] (11), [[htb-zetta]] (11), [[htb-interactive]] (11), [[htb-derailed]] (10), [[htb-sherlock-brutus]] (10), [[htb-trickster]] (9), [[htb-conversor]] (8), [[htb-facts]] (8), [[htb-monitored]] (8), [[htb-backendtwo]] (7), [[htb-enterprise]] (7), [[htb-overgraph]] (7), [[htb-backdoor]] (6), [[htb-bagel]] (6), [[htb-download]] (6), [[htb-editor]] (6), [[htb-mischief]] (6), [[htb-quick]] (5), [[htb-shared]] (5), [[htb-time]] (5), [[htb-bucket]] (4), [[htb-cybermonday]] (4), [[htb-forgot]] (4), [[htb-ghostlink]] (4), [[htb-helix]] (4), [[htb-jarmis]] (4), [[htb-mailroom]] (4), [[htb-overwatch]] (4), [[htb-pit]] (4), [[htb-sneakymailer]] (4), [[htb-sorcery]] (4), [[htb-yummy]] (4), [[htb-artificial]] (3), [[htb-broker]] (3), [[htb-chainsaw-rootkit]] (3)

_(y 54 mas)_

### path hijack _(tambien: path hijacking)_

9 maquinas.

[[htb-magic]] (3), [[htb-static]] (3), [[htb-gofer]] (2), [[htb-lazy]] (2), [[htb-pandora]] (2), [[htb-photobomb]] (2), [[htb-blockblock]] (1), [[htb-obscurity]] (1), [[htb-previse]] (1)

### ld_preload

4 maquinas.

[[htb-clicker]] (9), [[htb-surveillance]] (6), [[htb-chainsaw-rootkit]] (5), [[htb-dab]] (2)

### nfs no_root_squash _(tambien: no_root_squash)_

1 maquinas.

[[htb-fries]] (1)

### docker group

10 maquinas.

[[htb-kobold]] (3), [[htb-olympus]] (2), [[htb-ariekei]] (1), [[htb-cache]] (1), [[htb-feline]] (1), [[htb-laboratory]] (1), [[htb-mischief]] (1), [[htb-oz]] (1), [[htb-runner]] (1), [[htb-shoppy]] (1)

### lxd _(tambien: lxc)_

40 maquinas.

[[htb-tabby]] (37), [[htb-mischief]] (33), [[htb-obscurity]] (24), [[htb-brainfuck]] (21), [[htb-interactive]] (15), [[htb-carrier]] (8), [[htb-encoding]] (7), [[htb-calamity]] (6), [[htb-clicker]] (6), [[htb-kotarak]] (6), [[htb-iclean]] (5), [[htb-store]] (5), [[htb-book]] (4), [[htb-bookworm]] (4), [[htb-bucket]] (4), [[htb-ambassador]] (3), [[htb-backdoor]] (3), [[htb-caption]] (3), [[htb-chainsaw]] (3), [[htb-ouija]] (3), [[htb-overgraph]] (3), [[htb-patents]] (3), [[htb-talkative]] (3), [[htb-zero]] (3), [[htb-backendtwo]] (2), [[htb-corporate]] (2), [[htb-curling]] (2), [[htb-fingerprint]] (2), [[htb-haircut]] (2), [[htb-inception]] (2), [[htb-mango]] (2), [[htb-airtouch]] (1), [[htb-backend]] (1), [[htb-broker]] (1), [[htb-ellingson]] (1), [[htb-intuition]] (1), [[htb-jail]] (1), [[htb-ropetwo]] (1), [[htb-shoppy]] (1), [[htb-tenten]] (1)

### wildcard injection

3 maquinas.

[[htb-phoenix]] (3), [[htb-dump]] (1), [[htb-dynstr]] (1)

### kernel exploit

16 maquinas.

[[htb-bounty]] (5), [[htb-bastard]] (3), [[htb-devel]] (3), [[htb-undetected]] (3), [[htb-lame-more]] (2), [[htb-optimum]] (2), [[htb-aero]] (1), [[htb-bank]] (1), [[htb-blocky]] (1), [[htb-grandpa]] (1), [[htb-help]] (1), [[htb-hospital]] (1), [[htb-popcorn]] (1), [[htb-ropetwo]] (1), [[htb-twomillion]] (1), [[htb-valentine]] (1)

### dirty pipe _(tambien: cve-2022-0847)_

2 maquinas.

[[htb-altered]] (10), [[htb-interactive]] (2)

### pwnkit _(tambien: cve-2021-4034, pkexec)_

23 maquinas.

[[htb-paper]] (23), [[htb-interactive]] (14), [[htb-pressed]] (13), [[htb-routerspace]] (8), [[htb-altered]] (6), [[htb-antique]] (4), [[htb-mischief-more-root]] (2), [[htb-ouija]] (2), [[htb-bank]] (1), [[htb-cctv]] (1), [[htb-cerberus]] (1), [[htb-curling]] (1), [[htb-falafel]] (1), [[htb-fingerprint]] (1), [[htb-gofer]] (1), [[htb-haircut]] (1), [[htb-intentions]] (1), [[htb-irked]] (1), [[htb-laboratory]] (1), [[htb-mango]] (1), [[htb-october]] (1), [[htb-pandora]] (1), [[htb-passage]] (1)

### linpeas

25 maquinas.

[[htb-paper]] (13), [[htb-doctor]] (12), [[htb-cap]] (9), [[htb-interactive]] (9), [[htb-apocalyst]] (7), [[htb-routerspace]] (7), [[htb-time]] (7), [[htb-cronos]] (6), [[htb-traceback]] (3), [[htb-mailroom]] (2), [[htb-academy]] (1), [[htb-antique]] (1), [[htb-bank]] (1), [[htb-compromised]] (1), [[htb-earlyaccess]] (1), [[htb-forwardslash]] (1), [[htb-lame-more]] (1), [[htb-late]] (1), [[htb-mango]] (1), [[htb-monitored]] (1), [[htb-nineveh]] (1), [[htb-pwnbox-review]] (1), [[htb-shrek]] (1), [[htb-toby]] (1), [[htb-wifinetic]] (1)

### pspy

60 maquinas.

[[htb-interactive]] (38), [[htb-solidstate]] (16), [[htb-sorcery]] (10), [[htb-bamboo]] (9), [[htb-meta]] (9), [[htb-codify]] (8), [[htb-epsilon]] (8), [[htb-era]] (8), [[htb-inject]] (8), [[htb-jupiter]] (8), [[htb-opensource]] (8), [[htb-zero]] (8), [[htb-crossfit]] (7), [[htb-interface]] (7), [[htb-sandworm]] (7), [[htb-slonik]] (7), [[htb-toby]] (7), [[htb-topology]] (7), [[htb-lacasadepapel]] (6), [[htb-race]] (6), [[htb-stacked]] (6), [[htb-health]] (5), [[htb-aragog]] (4), [[htb-static]] (4), [[htb-awkward]] (3), [[htb-broscience]] (3), [[htb-catch]] (3), [[htb-celestial]] (3), [[htb-phoenix]] (3), [[htb-playertwo]] (3), [[htb-registrytwo]] (3), [[htb-shrek]] (3), [[htb-tartarsauce]] (3), [[htb-writeup]] (3), [[htb-fatty]] (2), [[htb-late]] (2), [[htb-nineveh]] (2), [[htb-ai]] (1), [[htb-alert]] (1), [[htb-book]] (1), [[htb-ctf]] (1), [[htb-curling]] (1), [[htb-download]] (1), [[htb-eureka]] (1), [[htb-friendzone]] (1), [[htb-ghoul]] (1), [[htb-laser]] (1), [[htb-monitorstwo]] (1), [[htb-patents]] (1), [[htb-player]] (1), [[htb-reddish]] (1), [[htb-redpanda]] (1), [[htb-response]] (1), [[htb-shared]] (1), [[htb-sunday]] (1), [[htb-teacher]] (1), [[htb-traceback]] (1), [[htb-unattended]] (1), [[htb-variatype]] (1), [[htb-writer]] (1)


## Movimiento lateral y ejecucion

### psexec

24 maquinas.

[[htb-sherlock-tracer]] (51), [[htb-interactive]] (12), [[htb-logging]] (9), [[htb-nest]] (6), [[htb-outdated]] (6), [[htb-active]] (3), [[htb-anubis]] (3), [[htb-remote]] (3), [[htb-atom]] (2), [[htb-darkzero]] (2), [[htb-flight]] (2), [[htb-jeeves]] (2), [[htb-netmon]] (2), [[htb-resolute]] (2), [[htb-sauna]] (2), [[htb-sherlock-campfire-1]] (2), [[htb-solarlab]] (2), [[htb-support]] (2), [[htb-apt]] (1), [[htb-control]] (1), [[htb-phantom]] (1), [[htb-search]] (1), [[htb-secnotes]] (1), [[htb-silo]] (1)

### wmiexec

19 maquinas.

[[htb-interactive]] (9), [[htb-hathor]] (5), [[htb-bruno]] (2), [[htb-forest]] (2), [[htb-intelligence]] (2), [[htb-pivotapi-more]] (2), [[htb-querier]] (2), [[htb-redelegate]] (2), [[htb-remote]] (2), [[htb-retrotwo]] (2), [[htb-rustykey]] (2), [[htb-search]] (2), [[htb-sizzle]] (2), [[htb-voleur]] (2), [[htb-vulncicada]] (2), [[htb-jab]] (1), [[htb-mist]] (1), [[htb-pirate]] (1), [[htb-sauna]] (1)

### dcomexec

2 maquinas.

[[htb-jab]] (7), [[htb-interactive]] (2)

### evil-winrm _(tambien: winrm)_

122 maquinas.

[[htb-object]] (144), [[htb-infiltrator]] (142), [[htb-rebound]] (114), [[htb-interactive]] (111), [[htb-pivotapi]] (105), [[htb-multimaster]] (101), [[htb-freelancer]] (99), [[htb-fulcrum]] (99), [[htb-nanocorp]] (94), [[htb-timelapse]] (91), [[htb-blackfield]] (90), [[htb-pirate]] (88), [[htb-overwatch]] (85), [[htb-absolute]] (79), [[htb-cascade]] (79), [[htb-heist]] (78), [[htb-coder]] (72), [[htb-darkcorp]] (72), [[htb-university]] (72), [[htb-administrator]] (70), [[htb-certificate]] (69), [[htb-eighteen]] (68), [[htb-puppy]] (68), [[htb-hospital]] (67), [[htb-driver]] (66), [[htb-logging]] (65), [[htb-haze]] (62), [[htb-sekhmet]] (62), [[htb-streamio]] (62), [[htb-cicada]] (60), [[htb-scepter]] (57), [[htb-support]] (57), [[htb-escape]] (55), [[htb-blazorized]] (54), [[htb-resolute]] (54), [[htb-appsanity]] (51), [[htb-fluffy]] (51), [[htb-office]] (51), [[htb-vintage]] (50), [[htb-baby]] (49), [[htb-sendai]] (49), [[htb-fuse]] (48), [[htb-tombwatcher]] (48), [[htb-mist]] (47), [[htb-apt]] (46), [[htb-sauna]] (46), [[htb-mirage]] (45), [[htb-rustykey]] (45), [[htb-ghost]] (44), [[htb-signed]] (44), [[htb-authority]] (43), [[htb-forest]] (43), [[htb-fries]] (42), [[htb-monteverde]] (42), [[htb-return]] (41), [[htb-sweep]] (41), [[htb-voleur]] (41), [[htb-mailing]] (37), [[htb-analysis]] (35), [[htb-certified]] (35)

_(y 62 mas)_

### ssh

413 maquinas.

[[htb-ghoul]] (129), [[htb-interactive]] (90), [[htb-attended]] (88), [[htb-resource]] (79), [[htb-snoopy]] (72), [[htb-corporate]] (63), [[htb-trick]] (58), [[htb-laser]] (57), [[htb-ypuffy]] (55), [[htb-skyfall]] (51), [[htb-registry]] (48), [[htb-earlyaccess]] (47), [[htb-principal]] (45), [[htb-store]] (44), [[htb-fingerprint]] (43), [[htb-player]] (42), [[htb-flujab]] (41), [[htb-vault]] (41), [[htb-facts]] (39), [[htb-barrier]] (38), [[htb-derailed]] (38), [[htb-fries]] (37), [[htb-sightless]] (37), [[htb-tartarsauce-part-2-backuperer-follow-up]] (37), [[htb-craft]] (36), [[htb-bookworm]] (35), [[htb-whiterabbit]] (35), [[htb-soulmate]] (34), [[htb-devzat]] (33), [[htb-late]] (32), [[htb-lacasadepapel]] (31), [[htb-pivotapi]] (31), [[htb-airtouch]] (30), [[htb-fatty]] (30), [[htb-postman]] (30), [[htb-ellingson]] (29), [[htb-imagery]] (29), [[htb-zetta]] (29), [[htb-blockblock]] (28), [[htb-code]] (28), [[htb-dyplesher]] (28), [[htb-ariekei]] (27), [[htb-carrier]] (27), [[htb-popcorn]] (27), [[htb-sherlock-brutus]] (27), [[htb-slonik]] (27), [[htb-builder]] (26), [[htb-cozyhosting]] (26), [[htb-guardian]] (26), [[htb-jupiter]] (26), [[htb-outbound]] (26), [[htb-quick]] (26), [[htb-response]] (26), [[htb-tentacle]] (26), [[htb-traverxec]] (26), [[htb-wifinetic]] (26), [[htb-drive]] (25), [[htb-flustered]] (25), [[htb-ropetwo]] (25), [[htb-sorcery]] (25)

_(y 353 mas)_

### rdp _(tambien: xfreerdp)_

54 maquinas.

[[htb-infiltrator]] (27), [[htb-lock]] (24), [[htb-nanocorp]] (19), [[htb-vulnescape]] (15), [[htb-interactive]] (14), [[htb-shibuya]] (12), [[htb-delegate]] (11), [[htb-reaper]] (11), [[htb-breach]] (10), [[htb-hospital]] (9), [[htb-hackback]] (8), [[htb-phantom]] (7), [[htb-axlle]] (6), [[htb-bruno]] (6), [[htb-retrotwo]] (6), [[htb-sendai]] (6), [[htb-jobtwo]] (5), [[htb-certificate]] (4), [[htb-signed]] (4), [[htb-voleur]] (4), [[htb-ghost]] (3), [[htb-ghostlink]] (3), [[htb-media]] (3), [[htb-redelegate]] (3), [[htb-sherlock-i-like-to]] (3), [[htb-acute]] (2), [[htb-babytwo]] (2), [[htb-bastion]] (2), [[htb-blazorized]] (2), [[htb-darkzero]] (2), [[htb-eighteen]] (2), [[htb-job]] (2), [[htb-mist]] (2), [[htb-object]] (2), [[htb-outdated]] (2), [[htb-pirate]] (2), [[htb-rainbow]] (2), [[htb-sweep]] (2), [[htb-barrier]] (1), [[htb-driver]] (1), [[htb-escapetwo]] (1), [[htb-forwardslash]] (1), [[htb-helpline-kali]] (1), [[htb-lustroustwo]] (1), [[htb-mailing]] (1), [[htb-overwatch]] (1), [[htb-pwnbox-review]] (1), [[htb-rebound]] (1), [[htb-reel2]] (1), [[htb-retro]] (1), [[htb-rustykey]] (1), [[htb-scepter]] (1), [[htb-sherlock-noxious]] (1), [[htb-solarlab]] (1)


## Pivoting y tuneles

### pivoting

21 maquinas.

[[chuleta-chisel]] (2), [[chuleta-tunneling]] (2), [[htb-administrator]] (1), [[htb-bamboo]] (1), [[htb-bighead]] (1), [[htb-carpediem]] (1), [[htb-darkzero]] (1), [[htb-dog]] (1), [[htb-eureka]] (1), [[htb-ghoul]] (1), [[htb-mailroom]] (1), [[htb-noter-alternative-root-first-blood]] (1), [[htb-overflow]] (1), [[htb-oz]] (1), [[htb-playertwo]] (1), [[htb-reddish]] (1), [[htb-search]] (1), [[htb-sherlock-bumblebee]] (1), [[htb-static]] (1), [[htb-toolbox]] (1), [[htb-vault]] (1)

### chisel

59 maquinas.

[[chuleta-chisel]] (52), [[htb-interactive]] (42), [[htb-antique]] (15), [[htb-talkative]] (12), [[htb-ghostlink]] (10), [[htb-anubis]] (9), [[htb-bitlab]] (9), [[htb-fulcrum]] (9), [[htb-carpediem]] (8), [[htb-cybermonday]] (8), [[htb-derailed]] (8), [[htb-opensource]] (8), [[htb-sendai]] (8), [[htb-appsanity]] (7), [[htb-bankrobber]] (7), [[htb-buff]] (7), [[htb-mentor]] (7), [[htb-moderators]] (6), [[htb-bighead]] (5), [[htb-cerberus]] (5), [[htb-darkzero]] (5), [[htb-feline]] (5), [[htb-hancliffe]] (5), [[htb-mist]] (5), [[htb-napper]] (5), [[htb-playertwo]] (5), [[htb-sizzle]] (5), [[htb-wifinetictwo]] (5), [[htb-arkham]] (4), [[htb-eighteen]] (4), [[htb-jab]] (4), [[htb-office]] (4), [[htb-onlyforyou]] (4), [[htb-pirate]] (4), [[htb-rainyday]] (4), [[htb-re]] (4), [[htb-signed]] (4), [[htb-solarlab]] (4), [[htb-toby]] (4), [[htb-university]] (4), [[htb-worker]] (4), [[chuleta-tunneling]] (4), [[htb-build]] (3), [[htb-flight]] (3), [[htb-infiltrator]] (3), [[htb-json]] (3), [[htb-breadcrumbs]] (2), [[htb-monitors]] (2), [[htb-pivotapi]] (2), [[htb-bigbang]] (1), [[htb-blockblock]] (1), [[htb-darkcorp]] (1), [[htb-magic]] (1), [[htb-monitorsthree]] (1), [[htb-omni]] (1), [[htb-pov]] (1), [[htb-registrytwo]] (1), [[htb-sorcery]] (1), [[htb-streamio]] (1)

### proxychains

35 maquinas.

[[htb-darkcorp]] (189), [[htb-darkzero]] (118), [[htb-ghostlink]] (110), [[htb-pirate]] (103), [[htb-university]] (81), [[htb-tentacle]] (79), [[htb-sekhmet]] (64), [[htb-airtouch]] (51), [[htb-mist]] (43), [[htb-signed]] (43), [[htb-rainyday]] (42), [[htb-carpediem]] (32), [[htb-inception]] (28), [[htb-anubis]] (26), [[htb-shibuya]] (22), [[htb-infiltrator]] (19), [[htb-bamboo]] (18), [[htb-build]] (17), [[htb-interactive]] (16), [[htb-pivotapi]] (14), [[htb-sendai]] (14), [[htb-hackback]] (13), [[htb-fulcrum]] (12), [[htb-feline]] (9), [[htb-fries]] (9), [[htb-hancliffe]] (9), [[htb-eighteen]] (8), [[htb-sizzle]] (5), [[htb-static]] (5), [[htb-toby]] (5), [[htb-poison]] (4), [[chuleta-tunneling]] (4), [[htb-cerberus]] (1), [[htb-moderators]] (1), [[chuleta-chisel]] (1)

### socat

22 maquinas.

[[htb-laser]] (15), [[htb-unattended]] (13), [[htb-redcross]] (11), [[htb-shibuya]] (11), [[htb-static]] (10), [[htb-interactive]] (9), [[htb-pirate]] (8), [[htb-feline]] (7), [[htb-ghoul]] (7), [[htb-joker]] (6), [[htb-reddish]] (6), [[htb-fatty]] (4), [[htb-overgraph]] (4), [[htb-worker]] (4), [[htb-mirage]] (3), [[htb-rebound]] (3), [[htb-smasher]] (3), [[htb-spooktrol]] (3), [[htb-cereal]] (2), [[htb-darkcorp]] (2), [[htb-armageddon]] (1), [[htb-bitlab]] (1)

### ssh tunnel _(tambien: port forwarding)_

36 maquinas.

[[chuleta-tunneling]] (4), [[htb-intense]] (3), [[htb-pivotapi]] (3), [[htb-hawk]] (2), [[htb-helix]] (2), [[htb-monitors]] (2), [[htb-poison]] (2), [[htb-reddish]] (2), [[htb-vault]] (2), [[htb-ai]] (1), [[htb-alert]] (1), [[htb-ariekei]] (1), [[htb-artificial]] (1), [[htb-backfire]] (1), [[htb-bigbang]] (1), [[htb-bighead]] (1), [[htb-bucket]] (1), [[htb-carpediem]] (1), [[htb-cereal-unintended]] (1), [[htb-derailed]] (1), [[htb-dynstr]] (1), [[htb-editor]] (1), [[htb-explore]] (1), [[htb-fingerprint]] (1), [[htb-flustered]] (1), [[htb-haystack]] (1), [[htb-irked]] (1), [[htb-noter-alternative-root-first-blood]] (1), [[htb-perspective]] (1), [[htb-planning]] (1), [[htb-rope]] (1), [[htb-ropetwo]] (1), [[htb-seventeen]] (1), [[htb-sizzle]] (1), [[htb-static]] (1), [[htb-watcher]] (1)

### tunnel

136 maquinas.

[[htb-interactive]] (50), [[htb-reddish]] (19), [[chuleta-tunneling]] (16), [[chuleta-chisel]] (13), [[htb-anubis]] (12), [[htb-kryptos]] (9), [[htb-mist]] (9), [[htb-bighead]] (8), [[htb-darkzero]] (8), [[htb-fulcrum]] (8), [[htb-intense]] (8), [[htb-pirate]] (8), [[htb-cerberus]] (7), [[htb-hancliffe]] (7), [[htb-store]] (7), [[htb-bankrobber]] (6), [[htb-derailed]] (6), [[htb-formulax]] (6), [[htb-hackback]] (6), [[htb-pivotapi]] (6), [[htb-sekhmet]] (6), [[htb-sendai]] (6), [[htb-worker]] (6), [[htb-antique]] (5), [[htb-bitlab]] (5), [[htb-buff]] (5), [[htb-carpediem]] (5), [[htb-flight]] (5), [[htb-mentor]] (5), [[htb-appsanity]] (4), [[htb-editor]] (4), [[htb-feline]] (4), [[htb-ghostlink]] (4), [[htb-ghoul]] (4), [[htb-json]] (4), [[htb-noter-alternative-root-first-blood]] (4), [[htb-opensource]] (4), [[htb-poison]] (4), [[htb-registry]] (4), [[htb-static]] (4), [[htb-talkative]] (4), [[htb-agile]] (3), [[htb-airtouch]] (3), [[htb-alert]] (3), [[htb-bigbang]] (3), [[htb-build]] (3), [[htb-caption]] (3), [[htb-darkcorp]] (3), [[htb-eighteen]] (3), [[htb-hawk]] (3), [[htb-helix]] (3), [[htb-infiltrator]] (3), [[htb-intuition]] (3), [[htb-moderators]] (3), [[htb-onlyforyou]] (3), [[htb-planning]] (3), [[htb-quick]] (3), [[htb-re]] (3), [[htb-sightless]] (3), [[htb-signed]] (3)

_(y 76 mas)_


## Servicios (por nombre)

### ftp

110 maquinas.

[[htb-sherlock-knock-knock]] (88), [[htb-pikaboo]] (72), [[htb-sorcery]] (62), [[htb-crossfit]] (57), [[htb-wifinetic]] (44), [[htb-intuition]] (39), [[htb-scavenger]] (38), [[htb-ten]] (34), [[htb-zetta]] (34), [[htb-fatty]] (31), [[htb-bruno]] (30), [[htb-devarea]] (30), [[htb-carrier]] (29), [[htb-chainsaw]] (28), [[htb-forge]] (27), [[htb-hawk]] (26), [[htb-json]] (25), [[htb-logforge]] (25), [[htb-metatwo]] (25), [[htb-noter]] (25), [[htb-reaper]] (24), [[htb-interactive]] (24), [[htb-aragog]] (23), [[htb-administrator]] (22), [[htb-oouch]] (22), [[htb-wingdata]] (22), [[htb-conceal]] (21), [[htb-era]] (21), [[htb-lame]] (21), [[htb-lustroustwo]] (21), [[htb-netmon]] (21), [[htb-response]] (20), [[htb-sightless]] (20), [[htb-redelegate]] (19), [[htb-sneakymailer]] (19), [[htb-tally]] (19), [[htb-access]] (18), [[htb-rainbow]] (18), [[htb-admirer]] (17), [[htb-devel]] (17), [[htb-inception]] (17), [[htb-luke]] (17), [[htb-pivotapi]] (17), [[htb-reel]] (17), [[htb-toolbox]] (17), [[htb-cap]] (15), [[htb-ethereal]] (15), [[htb-kotarak]] (15), [[htb-servmon]] (15), [[htb-dab]] (14), [[htb-lacasadepapel]] (14), [[htb-shrek]] (14), [[htb-forwardslash]] (13), [[htb-sherlock-i-like-to]] (12), [[htb-sizzle]] (11), [[htb-carpediem]] (8), [[htb-noter-alternative-root-first-blood]] (8), [[htb-remote]] (8), [[htb-attended]] (6), [[htb-blocky]] (6)

_(y 50 mas)_

### smb

160 maquinas.

[[htb-shibuya]] (602), [[htb-sendai]] (167), [[htb-infiltrator]] (152), [[htb-freelancer]] (148), [[htb-phantom]] (142), [[htb-babytwo]] (141), [[htb-haze]] (133), [[htb-cicada]] (123), [[chuleta-smb-enum]] (112), [[htb-flight]] (110), [[htb-pirate]] (109), [[htb-rebound]] (102), [[htb-breach]] (98), [[htb-retro]] (98), [[htb-vintage]] (94), [[htb-delegate]] (93), [[htb-sweep]] (85), [[htb-darkzero]] (80), [[htb-absolute]] (79), [[htb-streamio]] (77), [[htb-darkcorp]] (74), [[htb-mirage]] (74), [[htb-manager]] (72), [[htb-voleur]] (70), [[htb-puppy]] (67), [[htb-rustykey]] (66), [[htb-university]] (63), [[htb-administrator]] (62), [[htb-logging]] (61), [[htb-baby]] (59), [[htb-escapetwo]] (58), [[htb-mist]] (58), [[htb-multimaster]] (56), [[htb-ghostlink]] (54), [[htb-nanocorp]] (54), [[htb-search]] (54), [[htb-intelligence]] (50), [[htb-solarlab]] (50), [[htb-bruno]] (49), [[htb-apt]] (48), [[htb-cascade]] (48), [[htb-hathor]] (48), [[htb-office]] (48), [[htb-vulncicada]] (48), [[htb-jab]] (47), [[htb-tombwatcher]] (46), [[htb-authority]] (45), [[htb-resolute]] (45), [[htb-retrotwo]] (45), [[htb-thefrizz]] (45), [[htb-fuse]] (44), [[htb-mailing]] (40), [[htb-nest]] (39), [[htb-hospital]] (36), [[htb-analysis]] (35), [[htb-blue]] (35), [[htb-certified]] (34), [[htb-overwatch]] (34), [[htb-redelegate]] (34), [[htb-fluffy]] (32)

_(y 100 mas)_

### nfs

30 maquinas.

[[htb-slonik]] (135), [[htb-mirage]] (28), [[htb-jail]] (26), [[htb-squashed]] (17), [[htb-interactive]] (16), [[htb-fortune]] (13), [[htb-fries]] (13), [[htb-scepter]] (13), [[htb-clicker]] (10), [[htb-vulncicada]] (10), [[htb-remote]] (8), [[htb-corporate]] (7), [[htb-jobtwo]] (6), [[htb-voleur]] (4), [[htb-puppy]] (3), [[htb-bagel]] (1), [[htb-cobblestone]] (1), [[htb-darkcorp]] (1), [[htb-derailed]] (1), [[htb-flujab]] (1), [[htb-flustered]] (1), [[htb-giveback]] (1), [[htb-gofer]] (1), [[htb-intuition]] (1), [[htb-irked]] (1), [[htb-lame-more]] (1), [[htb-overwatch]] (1), [[htb-redcross]] (1), [[htb-sunday]] (1), [[htb-writeup]] (1)

### smtp

78 maquinas.

[[htb-flujab]] (45), [[htb-response]] (43), [[htb-solidstate]] (29), [[htb-mailing]] (27), [[htb-attended]] (23), [[htb-tentacle]] (21), [[htb-trick]] (17), [[htb-interactive]] (16), [[htb-sorcery]] (14), [[htb-gofer]] (12), [[htb-rabbit]] (11), [[htb-reel]] (11), [[htb-job]] (9), [[htb-silentium]] (9), [[htb-sneakymailer]] (9), [[htb-brainfuck]] (8), [[htb-jobtwo]] (8), [[htb-scavenger]] (8), [[htb-outbound]] (7), [[htb-outdated]] (7), [[htb-unattended]] (7), [[htb-axlle]] (6), [[htb-beep]] (6), [[htb-coder]] (6), [[htb-onlyforyou]] (6), [[htb-mailroom]] (5), [[htb-overflow]] (5), [[htb-redcross]] (5), [[htb-shibboleth]] (5), [[htb-data]] (4), [[htb-giveback]] (4), [[htb-metatwo]] (3), [[htb-nexus]] (3), [[htb-overwatch]] (3), [[htb-snoopy]] (3), [[htb-university]] (3), [[htb-writer]] (3), [[htb-crossfittwo]] (2), [[htb-dropzone]] (2), [[htb-friendzone]] (2), [[htb-linkvortex]] (2), [[htb-magicgardens]] (2), [[htb-openkeys]] (2), [[htb-pterodactyl]] (2), [[htb-scriptkiddie]] (2), [[htb-sherlock-knock-knock]] (2), [[htb-travel]] (2), [[htb-trickster]] (2), [[htb-alert]] (1), [[htb-awkward]] (1), [[htb-cat]] (1), [[htb-cctv]] (1), [[htb-crossfit]] (1), [[htb-cybermonday]] (1), [[htb-darkcorp]] (1), [[htb-driver]] (1), [[htb-editorial]] (1), [[htb-extension]] (1), [[htb-forwardslash]] (1), [[htb-ghost]] (1)

_(y 18 mas)_

### snmp

33 maquinas.

[[htb-intense]] (133), [[htb-underpass]] (78), [[htb-mentor]] (76), [[htb-pit]] (76), [[htb-airtouch]] (72), [[htb-monitored]] (48), [[htb-mischief]] (42), [[htb-interactive]] (34), [[htb-pandora]] (32), [[htb-formulax]] (25), [[htb-conceal]] (23), [[htb-sneaky]] (17), [[htb-monitorsthree]] (15), [[htb-carrier]] (10), [[htb-antique]] (8), [[htb-zipper]] (8), [[htb-sweep]] (4), [[htb-wall]] (4), [[htb-monitorstwo]] (3), [[htb-shibboleth]] (3), [[htb-monitors]] (2), [[htb-overwatch]] (2), [[htb-sherlock-knock-knock]] (2), [[htb-broker]] (1), [[htb-crossfittwo]] (1), [[htb-ghost]] (1), [[htb-giveback]] (1), [[htb-gofer]] (1), [[htb-intelligence]] (1), [[htb-mailing]] (1), [[htb-monitorsfour]] (1), [[htb-sherlock-meerkat]] (1), [[htb-wifinetic]] (1)

### pop3

20 maquinas.

[[htb-solidstate]] (13), [[htb-beep]] (7), [[htb-chaos]] (7), [[htb-mailing]] (5), [[htb-brainfuck]] (4), [[htb-tentacle]] (3), [[htb-giveback]] (2), [[htb-scriptkiddie]] (2), [[htb-university]] (2), [[htb-interactive]] (2), [[htb-driver]] (1), [[htb-forwardslash]] (1), [[htb-ghost]] (1), [[htb-giddy]] (1), [[htb-gofer]] (1), [[htb-querier]] (1), [[htb-reel2]] (1), [[htb-shibboleth]] (1), [[htb-sneakymailer]] (1), [[htb-trick]] (1)

### imap

32 maquinas.

[[htb-nexus]] (23), [[htb-sneakymailer]] (23), [[htb-chaos]] (14), [[htb-mailing]] (12), [[htb-outbound]] (12), [[htb-beep]] (9), [[htb-crimestoppers]] (9), [[htb-brainfuck]] (5), [[htb-mist]] (4), [[htb-giveback]] (3), [[htb-interactive]] (3), [[htb-darkcorp]] (2), [[htb-pirate]] (2), [[htb-signed]] (2), [[htb-university]] (2), [[htb-bart]] (1), [[htb-driver]] (1), [[htb-extension]] (1), [[htb-faculty]] (1), [[htb-forwardslash]] (1), [[htb-ghost]] (1), [[htb-giddy]] (1), [[htb-gofer]] (1), [[htb-hospital]] (1), [[htb-metatwo]] (1), [[htb-outdated]] (1), [[htb-photobomb]] (1), [[htb-querier]] (1), [[htb-reel2]] (1), [[htb-scavenger]] (1), [[htb-silo]] (1), [[htb-trickster]] (1)

### mssql

47 maquinas.

[[htb-signed]] (189), [[htb-pivotapi]] (73), [[htb-eighteen]] (68), [[htb-interactive]] (55), [[htb-querier]] (44), [[htb-escapetwo]] (39), [[htb-freelancer]] (33), [[htb-redelegate]] (31), [[htb-breach]] (25), [[htb-escape]] (22), [[htb-darkzero]] (21), [[htb-tally]] (20), [[htb-pivotapi-more]] (17), [[htb-overwatch]] (16), [[htb-scrambled-linux]] (16), [[htb-sendai]] (14), [[htb-manager]] (13), [[htb-scrambled-win]] (13), [[htb-ghost]] (8), [[htb-scrambled-beyond-root]] (8), [[htb-object]] (7), [[htb-streamio]] (7), [[htb-mantis]] (5), [[htb-pirate]] (4), [[htb-voleur]] (4), [[htb-fighter]] (3), [[htb-sherlock-campfire-1]] (3), [[htb-analytics]] (2), [[htb-mist]] (2), [[htb-multimaster]] (2), [[htb-scrambled]] (2), [[htb-blazorized]] (1), [[htb-certificate]] (1), [[htb-darkcorp]] (1), [[htb-giddy]] (1), [[htb-grandpa]] (1), [[htb-heal]] (1), [[htb-holiday]] (1), [[htb-jeeves]] (1), [[htb-jobtwo]] (1), [[htb-mailing]] (1), [[htb-monteverde]] (1), [[htb-outbound]] (1), [[htb-redcross]] (1), [[htb-search]] (1), [[htb-sherlock-meerkat]] (1), [[htb-university]] (1)

### mysql

182 maquinas.

[[htb-compromised]] (85), [[htb-yummy]] (60), [[htb-crossfit]] (51), [[htb-toby]] (51), [[htb-enterprise]] (44), [[htb-ambassador]] (43), [[htb-noter]] (36), [[htb-seventeen]] (34), [[htb-codify]] (33), [[htb-earlyaccess]] (33), [[htb-interactive]] (33), [[htb-magic]] (32), [[htb-monitorsthree]] (27), [[htb-flustered]] (26), [[htb-kryptos]] (26), [[htb-phoenix]] (26), [[htb-eureka]] (25), [[htb-craft]] (24), [[htb-falafel]] (23), [[htb-jarvis]] (23), [[htb-carpediem]] (21), [[htb-helix]] (20), [[htb-build]] (19), [[htb-nexus]] (19), [[htb-previse]] (19), [[htb-soccer]] (19), [[htb-aragog]] (17), [[htb-oz]] (17), [[htb-ai]] (16), [[htb-rabbit]] (16), [[htb-vessel]] (16), [[htb-certificate]] (15), [[htb-cobblestone]] (15), [[htb-unicode]] (15), [[htb-health]] (14), [[htb-sandworm]] (14), [[htb-shibboleth]] (14), [[htb-clicker]] (13), [[htb-noter-alternative-root-first-blood]] (13), [[htb-control]] (12), [[htb-dab]] (12), [[htb-thefrizz]] (12), [[htb-travel]] (12), [[htb-zipping]] (12), [[htb-academy]] (11), [[htb-breadcrumbs]] (11), [[htb-devvortex]] (11), [[htb-forgotten]] (11), [[htb-giveback]] (11), [[htb-guardian]] (11), [[htb-monitored]] (11), [[htb-sniper-beyondroot]] (11), [[htb-tenten]] (11), [[htb-usage]] (11), [[htb-busqueda]] (10), [[htb-cronos]] (10), [[htb-crossfittwo]] (10), [[htb-europa]] (10), [[htb-metatwo]] (10), [[htb-redcross]] (10)

_(y 122 mas)_

### postgresql

29 maquinas.

[[htb-darkcorp]] (34), [[htb-slonik]] (33), [[htb-zetta]] (25), [[htb-interactive]] (18), [[htb-download]] (17), [[htb-toolbox]] (12), [[htb-fries]] (9), [[htb-fortune]] (6), [[htb-jupiter]] (6), [[htb-monitored]] (5), [[htb-cozyhosting]] (4), [[htb-developer]] (4), [[htb-heal]] (4), [[htb-laboratory]] (4), [[htb-redcross]] (4), [[htb-broscience]] (3), [[htb-bitlab]] (2), [[htb-giveback]] (2), [[htb-interpreter]] (2), [[htb-jewel]] (2), [[htb-lantern]] (2), [[htb-mentor]] (2), [[htb-monitorsthree]] (2), [[htb-hawk]] (1), [[htb-holiday]] (1), [[htb-oz]] (1), [[htb-sherlock-meerkat]] (1), [[htb-waldo]] (1), [[htb-watcher]] (1)

### redis

40 maquinas.

[[htb-format]] (86), [[htb-shared]] (54), [[htb-postman]] (53), [[htb-reddish]] (44), [[htb-cybermonday]] (41), [[htb-atom]] (21), [[htb-catch]] (18), [[htb-interactive]] (18), [[htb-pollution]] (17), [[htb-pterodactyl]] (12), [[htb-nexus]] (9), [[htb-ready]] (8), [[htb-jewel]] (7), [[htb-environment]] (4), [[htb-sandworm]] (4), [[htb-travel]] (4), [[htb-crossfittwo]] (3), [[htb-data]] (3), [[htb-developer]] (3), [[htb-carrier]] (2), [[htb-freelancer]] (2), [[htb-laboratory]] (2), [[htb-sharp]] (2), [[htb-alert]] (1), [[htb-ariekei]] (1), [[htb-codetwo]] (1), [[htb-conversor]] (1), [[htb-escapetwo]] (1), [[htb-ethereal]] (1), [[htb-eureka]] (1), [[htb-giveback]] (1), [[htb-heist]] (1), [[htb-hospital]] (1), [[htb-lame]] (1), [[htb-lantern]] (1), [[htb-orion]] (1), [[htb-response]] (1), [[htb-snapped]] (1), [[htb-underpass]] (1), [[htb-university]] (1)

### mongodb

12 maquinas.

[[htb-formulax]] (9), [[htb-carpediem]] (8), [[htb-node]] (7), [[htb-nodeblog]] (7), [[htb-talkative]] (7), [[htb-mailroom]] (5), [[htb-stocker]] (3), [[htb-mango]] (2), [[htb-secret]] (2), [[htb-interactive]] (2), [[htb-editor]] (1), [[htb-overgraph]] (1)

### rsync

15 maquinas.

[[htb-zetta]] (79), [[htb-reddish]] (33), [[htb-unbalanced]] (24), [[htb-cobblestone]] (23), [[htb-build]] (13), [[htb-phoenix]] (8), [[htb-yummy]] (6), [[htb-interactive]] (6), [[htb-tentacle]] (2), [[htb-compromised]] (1), [[htb-derailed]] (1), [[htb-inception]] (1), [[htb-manage]] (1), [[htb-monitored]] (1), [[htb-pandora]] (1)

### tomcat

28 maquinas.

[[htb-manage]] (180), [[htb-strutted]] (107), [[htb-registrytwo]] (74), [[htb-seal]] (60), [[htb-tabby]] (50), [[htb-logforge]] (44), [[htb-kotarak]] (38), [[htb-stratosphere]] (36), [[htb-feline]] (35), [[htb-ophiuchi]] (26), [[htb-interactive]] (23), [[htb-arkham]] (19), [[htb-ai]] (15), [[htb-ghoul]] (13), [[htb-jerry]] (9), [[htb-barrier]] (7), [[htb-authority]] (2), [[htb-bizness]] (2), [[htb-cozyhosting]] (2), [[htb-eureka]] (2), [[htb-inject]] (2), [[htb-monitors]] (2), [[htb-bighead]] (1), [[htb-editor]] (1), [[htb-hancliffe]] (1), [[htb-helpline]] (1), [[htb-watcher]] (1), [[chuleta-smb-enum]] (1)

### jenkins

12 maquinas.

[[htb-build]] (118), [[htb-builder]] (98), [[htb-object]] (77), [[htb-interactive]] (20), [[htb-jeeves]] (14), [[htb-babytwo]] (5), [[htb-sink]] (5), [[htb-intentions]] (2), [[htb-moderators]] (2), [[htb-sendai]] (2), [[htb-shibuya]] (2), [[htb-sherlock-nubilum-1]] (1)

### apache

255 maquinas.

[[htb-manage]] (177), [[htb-zero]] (90), [[htb-cobblestone]] (81), [[htb-devarea]] (76), [[htb-quick]] (43), [[htb-guardian]] (42), [[htb-interpreter]] (42), [[htb-linkvortex]] (40), [[htb-interactive]] (36), [[htb-giveback]] (35), [[htb-gavel]] (32), [[htb-pandora]] (32), [[htb-pollution]] (29), [[htb-trickster]] (25), [[htb-bigbang]] (24), [[htb-forgotten]] (24), [[htb-clicker]] (23), [[htb-ghoul]] (23), [[htb-enterprise]] (22), [[htb-down]] (21), [[htb-europa]] (21), [[htb-gofer]] (21), [[htb-shocker]] (21), [[htb-ten]] (21), [[htb-cat]] (20), [[htb-crimestoppers]] (19), [[htb-ctf]] (19), [[htb-sightless]] (19), [[htb-alert]] (18), [[htb-earlyaccess]] (18), [[htb-broker]] (17), [[htb-networked]] (17), [[htb-armageddon]] (16), [[htb-logforge]] (16), [[htb-monitors]] (16), [[htb-playertwo]] (16), [[htb-strutted]] (16), [[htb-admirertoo]] (15), [[htb-overflow]] (15), [[htb-ai]] (14), [[htb-bucket]] (14), [[htb-hospital]] (14), [[htb-undetected]] (14), [[htb-jarvis]] (13), [[htb-kotarak]] (13), [[htb-openadmin]] (13), [[htb-watcher]] (13), [[htb-arkham]] (12), [[htb-encoding]] (12), [[htb-feline]] (12), [[htb-inception]] (12), [[htb-seventeen]] (12), [[htb-solidstate]] (12), [[htb-writer]] (12), [[htb-bizness]] (11), [[htb-codify]] (11), [[htb-doctor]] (11), [[htb-mischief]] (11), [[htb-onetwoseven]] (11), [[htb-permx]] (11)

_(y 195 mas)_

### nginx

152 maquinas.

[[htb-snapped]] (95), [[htb-steamcloud]] (54), [[htb-pikatwoo]] (41), [[htb-interactive]] (38), [[htb-pit]] (33), [[htb-bighead]] (29), [[htb-kobold]] (28), [[htb-broker]] (27), [[htb-spectra]] (27), [[htb-gobox]] (24), [[htb-format]] (22), [[htb-pikaboo]] (22), [[htb-fulcrum]] (21), [[htb-giveback]] (21), [[htb-hancliffe]] (20), [[htb-nexus]] (20), [[htb-pterodactyl]] (20), [[htb-variatype]] (20), [[htb-cybermonday]] (19), [[htb-sorcery]] (19), [[htb-fries]] (18), [[htb-skyfall]] (18), [[htb-silentium]] (17), [[htb-awkward]] (16), [[htb-dab]] (16), [[htb-sightless]] (16), [[htb-freelancer]] (15), [[htb-seal]] (15), [[htb-cypher]] (14), [[htb-monitorsfour]] (14), [[htb-soccer]] (14), [[htb-heal]] (13), [[htb-registry]] (13), [[htb-registrytwo]] (13), [[htb-thenotebook]] (13), [[htb-unattended]] (13), [[htb-planning]] (12), [[htb-sneakymailer]] (12), [[htb-static]] (12), [[htb-ariekei]] (11), [[htb-era]] (11), [[htb-formulax]] (11), [[htb-nocturnal]] (11), [[htb-orion]] (11), [[htb-trick]] (11), [[htb-backfire]] (10), [[htb-craft]] (10), [[htb-editor]] (10), [[htb-frolic]] (10), [[htb-hacknet]] (10), [[htb-monitorsthree]] (10), [[htb-response]] (10), [[htb-analytics]] (9), [[htb-artificial]] (9), [[htb-derailed]] (9), [[htb-drive]] (9), [[htb-flujab]] (9), [[htb-precious]] (9), [[htb-previous]] (9), [[htb-bolt]] (8)

_(y 92 mas)_

### iis

93 maquinas.

[[htb-overwatch]] (55), [[htb-interactive]] (26), [[htb-sherlock-i-like-to]] (24), [[htb-grandpa]] (21), [[htb-ghostlink]] (20), [[htb-napper]] (16), [[htb-search]] (16), [[htb-bruno]] (14), [[htb-cereal]] (14), [[htb-re]] (14), [[htb-streamio]] (13), [[htb-logging]] (12), [[htb-pov]] (12), [[htb-lustroustwo]] (11), [[htb-proper]] (11), [[htb-sizzle]] (11), [[htb-coder]] (10), [[htb-worker]] (10), [[htb-appsanity]] (9), [[htb-authority]] (9), [[htb-fighter]] (9), [[htb-granny]] (9), [[htb-job]] (9), [[htb-mailing]] (9), [[htb-perspective]] (9), [[htb-pirate]] (9), [[htb-rainbow]] (9), [[htb-breach]] (8), [[htb-crafty]] (8), [[htb-flight]] (8), [[htb-manager]] (8), [[htb-reaper]] (8), [[htb-redelegate]] (8), [[htb-tally]] (8), [[htb-aero]] (7), [[htb-analysis]] (7), [[htb-blazorized]] (7), [[htb-cereal-unintended]] (7), [[htb-minion]] (7), [[htb-object]] (7), [[htb-secnotes]] (7), [[htb-silo]] (7), [[htb-tombwatcher]] (7), [[htb-vulncicada]] (7), [[htb-absolute]] (6), [[htb-devel]] (6), [[htb-driver]] (6), [[htb-giddy]] (6), [[htb-rabbit]] (6), [[htb-reel2]] (6), [[htb-sendai]] (6), [[htb-axlle]] (5), [[htb-bastard]] (5), [[htb-bounty]] (5), [[htb-conceal]] (5), [[htb-hathor]] (5), [[htb-jeeves]] (5), [[htb-lock]] (5), [[htb-return]] (5), [[htb-anubis]] (4)

_(y 33 mas)_

### samba

32 maquinas.

[[htb-abducted]] (34), [[htb-lame]] (33), [[htb-ypuffy]] (27), [[htb-friendzone]] (12), [[htb-sniper]] (9), [[htb-writer]] (8), [[chuleta-smb-enum]] (8), [[htb-interactive]] (7), [[htb-help]] (6), [[htb-frolic]] (4), [[htb-falafel]] (3), [[htb-gofer]] (3), [[htb-node]] (3), [[htb-calamity]] (2), [[htb-lazy]] (2), [[htb-sekhmet]] (2), [[htb-smasher2]] (2), [[htb-zipper]] (2), [[htb-absolute]] (1), [[htb-bamboo]] (1), [[htb-brainfuck]] (1), [[htb-celestial]] (1), [[htb-jail]] (1), [[htb-kotarak]] (1), [[htb-lame-more]] (1), [[htb-overgraph]] (1), [[htb-passage]] (1), [[htb-puppy]] (1), [[htb-ropetwo]] (1), [[htb-sneaky]] (1), [[htb-tenten]] (1), [[htb-traceback]] (1)

### vnc

13 maquinas.

[[htb-poison]] (18), [[htb-helpline-kali]] (9), [[htb-intuition]] (7), [[htb-cascade]] (4), [[htb-voleur]] (4), [[htb-interactive]] (3), [[htb-lame-more]] (2), [[htb-sherlock-meerkat]] (2), [[htb-anubis]] (1), [[htb-barrier]] (1), [[htb-darkcorp]] (1), [[htb-ghostlink]] (1), [[htb-helpline]] (1)

### x11 forwarding _(tambien: x11forwarding)_

7 maquinas.

[[htb-store]] (3), [[htb-redcross]] (2), [[htb-gavel]] (1), [[htb-inject]] (1), [[htb-principal]] (1), [[htb-travel]] (1), [[htb-ypuffy]] (1)

### cups

10 maquinas.

[[htb-evilcups]] (56), [[htb-antique]] (21), [[htb-snapped]] (4), [[htb-interactive]] (3), [[htb-poison]] (2), [[htb-quick]] (2), [[htb-editor]] (1), [[htb-gofer]] (1), [[htb-solidstate]] (1), [[htb-toby]] (1)

### docker

151 maquinas.

[[htb-sorcery]] (176), [[htb-interactive]] (133), [[htb-feline]] (72), [[htb-monitorstwo]] (72), [[htb-stacked]] (72), [[htb-earlyaccess]] (69), [[htb-monitorsfour]] (65), [[htb-previous]] (55), [[htb-talkative]] (55), [[htb-fries]] (54), [[htb-registrytwo]] (54), [[htb-extension]] (52), [[htb-registry]] (47), [[htb-cybermonday]] (45), [[htb-data]] (40), [[htb-oz]] (35), [[htb-corporate]] (32), [[htb-toolbox]] (30), [[htb-enterprise]] (27), [[htb-monitorsthree]] (27), [[htb-ariekei]] (26), [[htb-kobold]] (26), [[htb-laboratory]] (26), [[htb-carpediem]] (20), [[htb-ghoul]] (20), [[htb-thenotebook]] (20), [[htb-busqueda]] (19), [[htb-catch]] (19), [[htb-artificial]] (16), [[htb-intuition]] (16), [[htb-opensource]] (16), [[htb-runner]] (16), [[htb-seventeen]] (15), [[htb-flustered]] (14), [[htb-magicgardens]] (14), [[htb-olympus]] (14), [[htb-response]] (14), [[htb-sink]] (13), [[htb-shoppy]] (12), [[htb-reddish]] (11), [[htb-bolt]] (10), [[htb-forgotten]] (10), [[htb-rainyday]] (10), [[htb-bigbang]] (9), [[htb-cypher]] (9), [[htb-ghost]] (9), [[htb-goodgames]] (9), [[htb-linkvortex]] (9), [[htb-mentor]] (9), [[htb-monitors]] (9), [[htb-sightless]] (9), [[htb-silentium]] (9), [[htb-cache]] (8), [[htb-facts]] (8), [[htb-patents]] (8), [[htb-travel]] (7), [[htb-visual]] (7), [[htb-bucket]] (6), [[htb-gobox]] (6), [[htb-planning]] (6)

_(y 91 mas)_

### kubernetes

11 maquinas.

[[htb-unobtainium]] (75), [[htb-giveback]] (71), [[htb-steamcloud]] (36), [[htb-pikatwoo]] (35), [[htb-interactive]] (9), [[htb-vessel]] (5), [[htb-cybermonday]] (1), [[htb-guardian]] (1), [[htb-laser]] (1), [[htb-monitorstwo]] (1), [[htb-sink]] (1)

### gitlab

30 maquinas.

[[htb-laboratory]] (90), [[htb-ready]] (60), [[htb-barrier]] (39), [[htb-bitlab]] (14), [[htb-ropetwo]] (9), [[htb-interactive]] (7), [[htb-travel]] (5), [[htb-blunder]] (3), [[htb-response]] (3), [[htb-data]] (2), [[htb-format]] (2), [[htb-soulmate]] (2), [[htb-bastion]] (1), [[htb-chainsaw]] (1), [[htb-cypher]] (1), [[htb-dyplesher]] (1), [[htb-encoding]] (1), [[htb-flujab]] (1), [[htb-hackback]] (1), [[htb-helpline-win]] (1), [[htb-intuition]] (1), [[htb-irked]] (1), [[htb-kryptos]] (1), [[htb-lacasadepapel]] (1), [[htb-meta]] (1), [[htb-object]] (1), [[htb-oouch]] (1), [[htb-rainbow]] (1), [[htb-rainyday]] (1), [[htb-worker]] (1)

### jira

2 maquinas.

[[htb-sink]] (5), [[htb-corporate]] (1)

### confluence

1 maquinas.

[[htb-sherlock-brutus]] (4)

### grafana

10 maquinas.

[[htb-data]] (112), [[htb-planning]] (46), [[htb-ambassador]] (37), [[htb-bigbang]] (24), [[htb-jupiter]] (9), [[htb-interactive]] (9), [[htb-barrier]] (1), [[htb-cerberus]] (1), [[htb-laboratory]] (1), [[htb-trickster]] (1)

### elasticsearch

5 maquinas.

[[htb-napper]] (4), [[htb-watcher]] (3), [[htb-interactive]] (3), [[htb-haystack]] (2), [[htb-admirertoo]] (1)

### wordpress

33 maquinas.

[[htb-giveback]] (117), [[htb-bigbang]] (59), [[htb-toby]] (59), [[htb-phoenix]] (41), [[htb-interactive]] (35), [[htb-enterprise]] (28), [[htb-pressed]] (22), [[htb-metatwo]] (20), [[htb-moderators]] (20), [[htb-tenten]] (18), [[htb-backdoor]] (15), [[htb-blocky]] (13), [[htb-monitors]] (13), [[htb-travel]] (10), [[htb-brainfuck]] (9), [[htb-paper]] (8), [[htb-spectra]] (7), [[htb-apocalyst]] (6), [[htb-tartarsauce]] (6), [[htb-tenet]] (6), [[htb-inception]] (5), [[htb-aragog]] (4), [[htb-chaos]] (4), [[htb-friendzone]] (3), [[htb-obscurity]] (3), [[htb-trickster]] (3), [[htb-admirer]] (1), [[htb-bart]] (1), [[htb-forgot]] (1), [[htb-hathor]] (1), [[htb-pikatwoo]] (1), [[htb-redelegate]] (1), [[htb-scavenger]] (1)

### drupal

8 maquinas.

[[htb-armageddon]] (66), [[htb-bastard]] (61), [[htb-hawk]] (32), [[htb-interactive]] (9), [[htb-pikatwoo]] (2), [[htb-dog]] (1), [[htb-hathor]] (1), [[htb-trickster]] (1)

### joomla

9 maquinas.

[[htb-devvortex]] (28), [[htb-office]] (20), [[htb-curling]] (19), [[htb-enterprise]] (17), [[htb-interactive]] (13), [[htb-rabbit]] (3), [[htb-hathor]] (1), [[htb-lazy]] (1), [[htb-phoenix]] (1)

### phpmyadmin

15 maquinas.

[[htb-scavenger]] (9), [[htb-fulcrum]] (7), [[htb-jarvis]] (7), [[htb-tartarsauce]] (6), [[htb-blocky]] (5), [[htb-nexus]] (3), [[htb-interactive]] (3), [[htb-nanocorp]] (2), [[htb-teacher]] (2), [[htb-bankrobber]] (1), [[htb-bighead]] (1), [[htb-breadcrumbs]] (1), [[htb-flight]] (1), [[htb-trickster]] (1), [[htb-visual]] (1)

### webdav

12 maquinas.

[[htb-inception]] (27), [[htb-grandpa]] (14), [[htb-granny]] (14), [[htb-pirate]] (7), [[htb-editor]] (6), [[htb-interactive]] (5), [[htb-data]] (2), [[htb-overwatch]] (2), [[htb-bighead]] (1), [[htb-bounty]] (1), [[htb-mist]] (1), [[htb-optimum]] (1)


## Vulnerabilidades web

### ssrf

42 maquinas.

[[htb-interactive]] (43), [[htb-backfire]] (16), [[htb-travel]] (10), [[htb-appsanity]] (9), [[htb-encoding]] (9), [[htb-heal]] (9), [[htb-writer]] (8), [[htb-cereal]] (7), [[htb-checker]] (6), [[htb-admirertoo]] (5), [[htb-bigbang]] (5), [[htb-devarea]] (5), [[htb-forge]] (5), [[htb-fulcrum]] (5), [[htb-lantern]] (5), [[htb-overgraph]] (5), [[htb-ready]] (5), [[htb-sau]] (5), [[htb-browsed]] (4), [[htb-cybermonday]] (4), [[htb-gofer]] (4), [[htb-jarmis]] (4), [[htb-love]] (4), [[htb-awkward]] (3), [[htb-editorial]] (3), [[htb-catch]] (2), [[htb-intentions]] (2), [[htb-intuition]] (2), [[htb-kotarak]] (2), [[htb-sea]] (2), [[htb-sorcery]] (2), [[htb-bountyhunter]] (1), [[htb-corporate]] (1), [[htb-down]] (1), [[htb-era]] (1), [[htb-health]] (1), [[htb-nocturnal]] (1), [[htb-perspective]] (1), [[htb-quick]] (1), [[htb-response]] (1), [[htb-schooled]] (1), [[htb-sightless]] (1)

### lfi _(tambien: local file inclusion)_

55 maquinas.

[[htb-interactive]] (31), [[htb-beep]] (12), [[htb-forwardslash]] (9), [[htb-nineveh]] (7), [[htb-variatype]] (7), [[htb-patents]] (6), [[htb-snoopy]] (6), [[htb-store]] (6), [[htb-zipping]] (6), [[htb-friendzone]] (5), [[htb-pikaboo]] (5), [[htb-tabby]] (5), [[htb-trick]] (5), [[htb-crimestoppers]] (4), [[htb-kobold]] (4), [[htb-pikatwoo]] (4), [[htb-pterodactyl]] (4), [[htb-sniper]] (4), [[htb-timing]] (4), [[htb-alert]] (3), [[htb-formulax]] (3), [[htb-pollution]] (3), [[htb-encoding]] (2), [[htb-haystack]] (2), [[htb-inception]] (2), [[htb-jarvis]] (2), [[htb-lacasadepapel]] (2), [[htb-mailing]] (2), [[htb-poison]] (2), [[htb-popcorn]] (2), [[htb-travel]] (2), [[htb-trickster]] (2), [[htb-unattended]] (2), [[htb-unobtainium]] (2), [[htb-updown]] (2), [[htb-valentine]] (2), [[htb-bagel]] (1), [[htb-bart]] (1), [[htb-broscience]] (1), [[htb-cache]] (1), [[htb-cerberus]] (1), [[htb-corporate]] (1), [[htb-cronos]] (1), [[htb-earlyaccess]] (1), [[htb-guardian]] (1), [[htb-helpline-win]] (1), [[htb-helpline]] (1), [[htb-kotarak]] (1), [[htb-monitors]] (1), [[htb-ouija]] (1), [[htb-planning]] (1), [[htb-retired]] (1), [[htb-seventeen]] (1), [[htb-thefrizz]] (1), [[htb-whiterabbit]] (1)

### rfi _(tambien: remote file inclusion)_

14 maquinas.

[[htb-interactive]] (7), [[htb-forwardslash]] (5), [[htb-sniper]] (4), [[htb-tartarsauce]] (4), [[htb-cache]] (3), [[htb-flight]] (1), [[htb-guardian]] (1), [[htb-moderators]] (1), [[htb-pandora]] (1), [[htb-poison]] (1), [[htb-proper]] (1), [[htb-streamio]] (1), [[htb-swagshop]] (1), [[htb-trickster]] (1)

### sqli _(tambien: sql injection)_

186 maquinas.

[[htb-interactive]] (173), [[htb-drive]] (80), [[htb-corporate]] (49), [[htb-lantern]] (46), [[htb-cascade]] (38), [[htb-overwatch]] (34), [[htb-heal]] (29), [[htb-infiltrator]] (27), [[htb-retired]] (27), [[htb-artificial]] (25), [[htb-sherlock-bumblebee]] (23), [[htb-breadcrumbs]] (20), [[htb-cobblestone]] (19), [[htb-data]] (19), [[htb-pilgrimage]] (18), [[htb-codetwo]] (17), [[htb-era]] (17), [[htb-intense]] (17), [[htb-spooktrol]] (17), [[htb-streamio]] (17), [[htb-cat]] (16), [[htb-dyplesher]] (16), [[htb-hancliffe]] (16), [[htb-kryptos]] (15), [[htb-pc]] (15), [[htb-phoenix]] (15), [[htb-university]] (14), [[htb-code]] (13), [[htb-codify]] (13), [[htb-giveback]] (13), [[htb-holiday]] (13), [[htb-jarvis]] (13), [[htb-monitorsthree]] (13), [[htb-sherlock-subatomic]] (13), [[htb-writer]] (13), [[htb-bolt]] (12), [[htb-compiled]] (12), [[htb-dump]] (12), [[htb-charon]] (11), [[htb-health]] (11), [[htb-rabbit]] (11), [[htb-secnotes]] (11), [[htb-sherlock-tick-tock]] (11), [[htb-toby]] (11), [[htb-crossfittwo]] (10), [[htb-fingerprint]] (10), [[htb-ghost]] (10), [[htb-registry]] (10), [[htb-trick]] (10), [[htb-unattended]] (10), [[htb-bigbang]] (9), [[htb-bookworm]] (9), [[htb-derailed]] (9), [[htb-environment]] (9), [[htb-fatty]] (9), [[htb-fortune]] (9), [[htb-metatwo]] (9), [[htb-sekhmet]] (9), [[htb-snapped]] (9), [[htb-titanic]] (9)

_(y 126 mas)_

### xxe

18 maquinas.

[[htb-bountyhunter]] (23), [[htb-pollution]] (17), [[htb-patents]] (16), [[htb-interactive]] (16), [[htb-re]] (10), [[htb-aragog]] (7), [[htb-devoops]] (7), [[htb-forwardslash]] (7), [[htb-fulcrum]] (7), [[htb-snoopy]] (7), [[htb-spider]] (7), [[htb-clicker]] (5), [[htb-nodeblog]] (5), [[htb-redpanda]] (5), [[htb-metatwo]] (4), [[htb-helpline]] (3), [[htb-conversor]] (2), [[htb-doctor]] (1)

### ssti _(tambien: template injection)_

34 maquinas.

[[htb-interactive]] (37), [[htb-hacknet]] (36), [[htb-sandworm]] (22), [[htb-bolt]] (18), [[htb-late]] (10), [[htb-oz]] (10), [[htb-spider]] (10), [[htb-doctor]] (9), [[htb-gobox]] (9), [[htb-epsilon]] (7), [[htb-goodgames]] (7), [[htb-redpanda]] (7), [[htb-flustered]] (6), [[htb-iclean]] (6), [[htb-perfection]] (6), [[htb-cobblestone]] (5), [[htb-nunchucks]] (4), [[htb-overgraph]] (4), [[htb-race]] (4), [[htb-trickster]] (4), [[htb-anubis]] (3), [[htb-catch]] (3), [[htb-sightless]] (3), [[htb-talkative]] (3), [[htb-chemistry]] (2), [[htb-codetwo]] (2), [[htb-hancliffe]] (2), [[htb-headless]] (2), [[htb-nodeblog]] (2), [[htb-store]] (2), [[htb-format]] (1), [[htb-interpreter]] (1), [[htb-orion]] (1), [[htb-shrek]] (1)

### deserialization

53 maquinas.

[[htb-interactive]] (62), [[htb-arkham]] (8), [[htb-cereal]] (8), [[htb-ophiuchi]] (7), [[htb-perspective]] (7), [[htb-bigbang]] (6), [[htb-celestial]] (5), [[htb-nodeblog]] (5), [[htb-blurry]] (4), [[htb-cybermonday]] (4), [[htb-fatty]] (4), [[htb-interpreter]] (4), [[htb-jewel]] (4), [[htb-json]] (4), [[htb-outbound]] (4), [[htb-registrytwo]] (4), [[htb-tenet]] (4), [[htb-travel]] (4), [[htb-chemistry]] (3), [[htb-cronos]] (3), [[htb-darkcorp]] (3), [[htb-devoops]] (3), [[htb-horizontall]] (3), [[htb-player]] (3), [[htb-scrambled-linux]] (3), [[htb-scrambled-win]] (3), [[htb-sekhmet]] (3), [[htb-artificial]] (2), [[htb-broscience]] (2), [[htb-developer]] (2), [[htb-hacknet]] (2), [[htb-laser]] (2), [[htb-manage]] (2), [[htb-monitors]] (2), [[htb-precious]] (2), [[htb-sharp]] (2), [[htb-sherlock-i-like-to]] (2), [[htb-academy]] (1), [[htb-arctic]] (1), [[htb-broker]] (1), [[htb-canape]] (1), [[htb-catch]] (1), [[htb-feline]] (1), [[htb-fingerprint]] (1), [[htb-gavel]] (1), [[htb-giveback]] (1), [[htb-laboratory]] (1), [[htb-magicgardens]] (1), [[htb-pandora]] (1), [[htb-scrambled]] (1), [[htb-sorcery]] (1), [[htb-swagshop]] (1), [[htb-time]] (1)

### command injection

112 maquinas.

[[htb-awkward]] (8), [[htb-cronos]] (8), [[htb-fortune]] (8), [[htb-intuition]] (8), [[htb-scriptkiddie]] (8), [[htb-cctv]] (7), [[htb-stacked]] (7), [[htb-writer]] (7), [[htb-dynstr]] (6), [[htb-imagery]] (6), [[htb-openkeys]] (6), [[htb-secret]] (6), [[htb-backfire]] (5), [[htb-bigbang]] (5), [[htb-crossfit]] (5), [[htb-cypher]] (5), [[htb-devarea]] (5), [[htb-devzat]] (5), [[htb-doctor]] (5), [[htb-fingerprint]] (5), [[htb-ghost]] (5), [[htb-nocturnal]] (5), [[htb-photobomb]] (5), [[htb-variatype]] (5), [[htb-broscience]] (4), [[htb-caption]] (4), [[htb-cozyhosting]] (4), [[htb-formulax]] (4), [[htb-headless]] (4), [[htb-holiday]] (4), [[htb-horizontall]] (4), [[htb-mischief]] (4), [[htb-netmon]] (4), [[htb-noter]] (4), [[htb-overwatch]] (4), [[htb-pilgrimage]] (4), [[htb-player]] (4), [[htb-previse]] (4), [[htb-sekhmet]] (4), [[htb-unobtainium]] (4), [[htb-abducted]] (3), [[htb-catch]] (3), [[htb-charon]] (3), [[htb-cobblestone]] (3), [[htb-ethereal]] (3), [[htb-extension]] (3), [[htb-haircut]] (3), [[htb-jarvis]] (3), [[htb-late]] (3), [[htb-mentor]] (3), [[htb-meta]] (3), [[htb-monitorstwo]] (3), [[htb-oouch]] (3), [[htb-perspective]] (3), [[htb-reset]] (3), [[htb-routerspace]] (3), [[htb-sea]] (3), [[htb-surveillance]] (3), [[htb-twomillion]] (3), [[htb-zero]] (3)

_(y 52 mas)_

### file upload _(tambien: upload bypass)_

68 maquinas.

[[htb-spooktrol]] (9), [[htb-arctic]] (7), [[htb-reddish]] (4), [[htb-strutted]] (4), [[htb-tartarsauce]] (4), [[htb-blunder]] (3), [[htb-crimestoppers]] (3), [[htb-help]] (3), [[htb-nibbles]] (3), [[htb-phoenix]] (3), [[htb-surveillance]] (3), [[htb-cache]] (2), [[htb-certificate]] (2), [[htb-falafel]] (2), [[htb-ghoul]] (2), [[htb-intentions]] (2), [[htb-lantern]] (2), [[htb-logging]] (2), [[htb-media]] (2), [[htb-nexus]] (2), [[htb-retired]] (2), [[htb-soulmate]] (2), [[htb-admirertoo]] (1), [[htb-appsanity]] (1), [[htb-bart]] (1), [[htb-bigbang]] (1), [[htb-carpediem]] (1), [[htb-cereal]] (1), [[htb-chaos]] (1), [[htb-charon]] (1), [[htb-compromised]] (1), [[htb-cronos]] (1), [[htb-encoding]] (1), [[htb-era]] (1), [[htb-forge]] (1), [[htb-frolic]] (1), [[htb-hackback]] (1), [[htb-hathor]] (1), [[htb-haze]] (1), [[htb-hospital]] (1), [[htb-infiltrator]] (1), [[htb-love]] (1), [[htb-magic]] (1), [[htb-mirage]] (1), [[htb-moderators]] (1), [[htb-monitorsthree]] (1), [[htb-nanocorp]] (1), [[htb-networked]] (1), [[htb-nocturnal]] (1), [[htb-onetwoseven]] (1), [[htb-passage]] (1), [[htb-permx]] (1), [[htb-perspective]] (1), [[htb-pilgrimage]] (1), [[htb-pit]] (1), [[htb-pterodactyl]] (1), [[htb-ransom]] (1), [[htb-registry]] (1), [[htb-sendai]] (1), [[htb-seventeen]] (1)

_(y 8 mas)_

### jwt

51 maquinas.

[[htb-interactive]] (53), [[htb-principal]] (39), [[htb-secret]] (30), [[htb-cereal]] (29), [[htb-backendtwo]] (28), [[htb-cybermonday]] (23), [[htb-blazorized]] (22), [[htb-awkward]] (21), [[htb-yummy]] (19), [[htb-sorcery]] (16), [[htb-unicode]] (15), [[htb-backend]] (13), [[htb-craft]] (13), [[htb-corporate]] (12), [[htb-player]] (11), [[htb-breadcrumbs]] (10), [[htb-oz]] (10), [[htb-devzat]] (9), [[htb-pollution]] (9), [[htb-artificial]] (8), [[htb-thenotebook]] (7), [[htb-epsilon]] (6), [[htb-fingerprint]] (6), [[htb-data]] (5), [[htb-formulax]] (5), [[htb-backfire]] (4), [[htb-appsanity]] (3), [[htb-caption]] (3), [[htb-instant]] (3), [[htb-ghost]] (2), [[htb-horizontall]] (2), [[htb-intuition]] (2), [[htb-luke]] (2), [[htb-noter]] (2), [[htb-pikatwoo]] (2), [[htb-rainyday]] (2), [[htb-sink]] (2), [[htb-blockblock]] (1), [[htb-checker]] (1), [[htb-doctor]] (1), [[htb-eureka]] (1), [[htb-giveback]] (1), [[htb-heal]] (1), [[htb-iclean]] (1), [[htb-mentor]] (1), [[htb-overgraph]] (1), [[htb-pc]] (1), [[htb-registrytwo]] (1), [[htb-spider]] (1), [[htb-variatype]] (1), [[htb-wifinetictwo]] (1)

### idor

17 maquinas.

[[htb-interactive]] (15), [[htb-era]] (6), [[htb-bookworm]] (5), [[htb-drive]] (4), [[htb-guardian]] (4), [[htb-rainyday]] (4), [[htb-cap]] (3), [[htb-nocturnal]] (3), [[htb-extension]] (2), [[htb-moderators]] (2), [[htb-agile]] (1), [[htb-cobblestone]] (1), [[htb-corporate]] (1), [[htb-derailed]] (1), [[htb-freelancer]] (1), [[htb-gavel]] (1), [[htb-noter]] (1)

### xss

104 maquinas.

[[htb-interactive]] (56), [[htb-formulax]] (36), [[htb-derailed]] (27), [[htb-stacked]] (26), [[htb-bookworm]] (18), [[htb-crossfit]] (18), [[htb-sorcery]] (17), [[htb-cereal]] (16), [[htb-book]] (15), [[htb-fingerprint]] (14), [[htb-bankrobber]] (12), [[htb-cobblestone]] (12), [[htb-sea]] (12), [[htb-alert]] (11), [[htb-data]] (11), [[htb-cat]] (9), [[htb-guardian]] (9), [[htb-mailroom]] (9), [[htb-trickster]] (9), [[htb-bigbang]] (8), [[htb-darkcorp]] (7), [[htb-extension]] (7), [[htb-intuition]] (7), [[htb-ambassador]] (6), [[htb-earlyaccess]] (6), [[htb-facts]] (6), [[htb-imagery]] (6), [[htb-magicgardens]] (6), [[htb-redcross]] (6), [[htb-sightless]] (6), [[htb-caption]] (5), [[htb-eureka]] (5), [[htb-headless]] (5), [[htb-holiday]] (5), [[htb-overgraph]] (5), [[htb-anubis]] (4), [[htb-blockblock]] (4), [[htb-forgot]] (4), [[htb-iclean]] (4), [[htb-schooled]] (4), [[htb-carpediem]] (3), [[htb-corporate]] (3), [[htb-giveback]] (3), [[htb-intentions]] (3), [[htb-jupiter]] (3), [[htb-oouch]] (3), [[htb-ropetwo]] (3), [[htb-stocker]] (3), [[htb-backdoor]] (2), [[htb-clicker]] (2), [[htb-cozyhosting]] (2), [[htb-hacknet]] (2), [[htb-kobold]] (2), [[htb-monitorsthree]] (2), [[htb-talkative]] (2), [[htb-toby]] (2), [[htb-wingdata]] (2), [[htb-analysis]] (1), [[htb-analytics]] (1), [[htb-apocalyst]] (1)

_(y 44 mas)_

### csrf

47 maquinas.

[[htb-hacknet]] (38), [[htb-guardian]] (22), [[htb-crossfittwo]] (13), [[htb-earlyaccess]] (12), [[htb-oouch]] (11), [[htb-crimestoppers]] (10), [[htb-monitors]] (10), [[htb-surveillance]] (10), [[htb-bart]] (9), [[htb-extension]] (9), [[htb-wall]] (9), [[htb-interactive]] (9), [[htb-blunder]] (8), [[htb-drive]] (8), [[htb-sightless]] (8), [[htb-orion]] (7), [[htb-overgraph]] (7), [[htb-crossfit]] (6), [[htb-checker]] (5), [[htb-nocturnal]] (5), [[htb-corporate]] (4), [[htb-sense]] (4), [[htb-formulax]] (3), [[htb-magicgardens]] (3), [[htb-trickster]] (3), [[htb-university]] (3), [[htb-carpediem]] (2), [[htb-darkcorp]] (2), [[htb-doctor]] (2), [[htb-frolic]] (2), [[htb-health]] (2), [[htb-intentions]] (2), [[htb-manage]] (2), [[htb-ransom]] (2), [[htb-bamboo]] (1), [[htb-derailed]] (1), [[htb-developer]] (1), [[htb-facts]] (1), [[htb-freelancer]] (1), [[htb-hospital]] (1), [[htb-nexus]] (1), [[htb-nineveh]] (1), [[htb-perspective]] (1), [[htb-response]] (1), [[htb-sherlock-i-like-to]] (1), [[htb-solarlab]] (1), [[htb-soulmate]] (1)

### log4shell _(tambien: log4j)_

10 maquinas.

[[htb-crafty]] (19), [[htb-logforge]] (17), [[htb-watcher]] (10), [[htb-interactive]] (6), [[htb-interpreter]] (5), [[htb-fatty]] (3), [[htb-haystack]] (3), [[htb-strutted]] (2), [[htb-ethereal]] (1), [[htb-nodeblog]] (1)

### shellshock

4 maquinas.

[[htb-shocker]] (16), [[htb-ariekei]] (12), [[htb-beep]] (5), [[htb-interactive]] (4)

### struts

5 maquinas.

[[htb-strutted]] (21), [[htb-stratosphere]] (11), [[htb-interactive]] (3), [[htb-celestial]] (1), [[htb-trickster]] (1)


## Credenciales y loot

### gpp _(tambien: cpassword, group policy preferences)_

3 maquinas.

[[htb-active]] (10), [[htb-interactive]] (6), [[htb-querier]] (4)


## Metodologia y explotacion generica

### reverse shell

348 maquinas.

[[htb-static]] (10), [[htb-sherlock-pikaptcha]] (9), [[htb-monitors]] (8), [[htb-aero]] (7), [[htb-fighter]] (7), [[htb-trickster]] (7), [[htb-wifinetictwo]] (7), [[htb-axlle]] (6), [[htb-calamity]] (6), [[htb-silentium]] (6), [[htb-solidstate]] (6), [[htb-updown]] (6), [[htb-attended]] (5), [[htb-cobblestone]] (5), [[htb-darkzero]] (5), [[htb-formulax]] (5), [[htb-inception]] (5), [[htb-monitorsfour]] (5), [[htb-monitorsthree]] (5), [[htb-pit]] (5), [[htb-reddish]] (5), [[htb-retired]] (5), [[htb-zipper]] (5), [[htb-acute]] (4), [[htb-appsanity]] (4), [[htb-ariekei]] (4), [[htb-blockblock]] (4), [[htb-charon]] (4), [[htb-fortune]] (4), [[htb-hancliffe]] (4), [[htb-hathor]] (4), [[htb-hospital]] (4), [[htb-meta]] (4), [[htb-mischief]] (4), [[htb-moderators]] (4), [[htb-opensource]] (4), [[htb-oz]] (4), [[htb-phoenix]] (4), [[htb-pikatwoo]] (4), [[htb-rainbow]] (4), [[htb-scavenger]] (4), [[htb-sorcery]] (4), [[htb-talkative]] (4), [[htb-time]] (4), [[htb-toby]] (4), [[htb-visual]] (4), [[htb-airtouch]] (3), [[htb-antique]] (3), [[htb-arctic]] (3), [[htb-artificial]] (3), [[htb-blazorized]] (3), [[htb-caption]] (3), [[htb-carpediem]] (3), [[htb-chaos]] (3), [[htb-compiled]] (3), [[htb-ctf]] (3), [[htb-devarea]] (3), [[htb-doctor]] (3), [[htb-dyplesher]] (3), [[htb-enterprise]] (3)

_(y 288 mas)_

### bind shell

1 maquinas.

[[htb-faculty]] (1)

### buffer overflow

41 maquinas.

[[htb-buff]] (12), [[htb-bigbang]] (6), [[htb-calamity]] (6), [[htb-retired]] (4), [[htb-smasher]] (4), [[htb-bighead]] (3), [[htb-derailed]] (3), [[htb-grandpa]] (3), [[htb-jail]] (3), [[htb-lame]] (3), [[htb-october]] (3), [[htb-patents]] (3), [[htb-attended]] (2), [[htb-intense]] (2), [[htb-magicgardens]] (2), [[htb-node]] (2), [[htb-reaper]] (2), [[htb-registry]] (2), [[htb-routerspace]] (2), [[htb-sneaky]] (2), [[htb-bankrobber]] (1), [[htb-bighead-bof]] (1), [[htb-bounty]] (1), [[htb-chatterbox]] (1), [[htb-drive]] (1), [[htb-enterprise]] (1), [[htb-hancliffe]] (1), [[htb-optimum]] (1), [[htb-orion]] (1), [[htb-overflow]] (1), [[htb-paper]] (1), [[htb-playertwo]] (1), [[htb-rainbow]] (1), [[htb-redcross]] (1), [[htb-rope]] (1), [[htb-safe]] (1), [[htb-sandworm]] (1), [[htb-smasher-bof]] (1), [[htb-smasher2]] (1), [[htb-snoopy]] (1), [[chuleta-smb-enum]] (1)

### cve-

215 maquinas.

[[htb-interactive]] (578), [[htb-outbound]] (21), [[htb-watcher]] (21), [[htb-giveback]] (20), [[htb-orion]] (20), [[htb-soulmate]] (19), [[htb-meta]] (17), [[htb-routerspace]] (17), [[htb-conversor]] (16), [[htb-driver]] (16), [[htb-feline]] (16), [[htb-pilgrimage]] (16), [[htb-paper]] (15), [[htb-interpreter]] (14), [[htb-pterodactyl]] (14), [[htb-twomillion]] (14), [[htb-darkcorp]] (13), [[htb-monitorstwo]] (13), [[htb-openkeys]] (13), [[htb-planning]] (13), [[htb-snoopy]] (13), [[htb-variatype]] (13), [[htb-aero]] (12), [[htb-codify]] (12), [[htb-hospital]] (12), [[htb-mailing]] (12), [[htb-pikatwoo]] (12), [[htb-silentium]] (12), [[htb-snapped]] (12), [[htb-thenotebook]] (12), [[htb-catch]] (11), [[htb-wingdata]] (11), [[htb-formulax]] (10), [[htb-monitorsfour]] (10), [[htb-nocturnal]] (10), [[htb-sherlock-meerkat]] (10), [[htb-bigbang]] (9), [[htb-canape]] (9), [[htb-cerberus]] (9), [[htb-darkzero]] (9), [[htb-devvortex]] (9), [[htb-expressway]] (9), [[htb-facts]] (9), [[htb-horizontall]] (9), [[htb-nanocorp]] (9), [[htb-cctv]] (8), [[htb-fluffy]] (8), [[htb-kobold]] (8), [[htb-nexus]] (8), [[htb-office]] (8), [[htb-outdated]] (8), [[htb-race]] (8), [[htb-reel]] (8), [[htb-runner]] (8), [[htb-sightless]] (8), [[htb-solarlab]] (8), [[htb-trickster]] (8), [[htb-antique]] (7), [[htb-checker]] (7), [[htb-devarea]] (7)

_(y 155 mas)_

### public exploit _(tambien: exploit-db)_

27 maquinas.

[[htb-interactive]] (11), [[htb-zipper]] (9), [[htb-noter]] (4), [[htb-buff]] (2), [[htb-chatterbox]] (2), [[htb-snoopy]] (2), [[htb-wall]] (2), [[chuleta-chisel]] (2), [[htb-armageddon]] (1), [[htb-backdoor]] (1), [[htb-bolt]] (1), [[htb-compromised]] (1), [[htb-crafty]] (1), [[htb-formulax]] (1), [[htb-frolic]] (1), [[htb-grandpa]] (1), [[htb-hawk]] (1), [[htb-helpline-kali]] (1), [[htb-knife]] (1), [[htb-october]] (1), [[htb-openadmin]] (1), [[htb-optimum]] (1), [[htb-phoenix]] (1), [[htb-popcorn]] (1), [[htb-servmon]] (1), [[htb-tentacle]] (1), [[htb-vessel]] (1)

### hashcat

192 maquinas.

[[htb-interactive]] (158), [[htb-magicgardens]] (16), [[htb-bizness]] (14), [[htb-streamio]] (14), [[htb-bigbang]] (12), [[htb-certificate]] (12), [[htb-moderators]] (12), [[htb-awkward]] (11), [[htb-instant]] (11), [[htb-ghostlink]] (10), [[htb-broscience]] (9), [[htb-compiled]] (9), [[htb-sightless]] (9), [[htb-sizzle]] (9), [[htb-administrator]] (8), [[htb-derailed]] (8), [[htb-jail]] (8), [[htb-perfection]] (8), [[htb-pivotapi]] (8), [[htb-toby]] (8), [[htb-data]] (7), [[htb-devvortex]] (7), [[htb-infiltrator]] (7), [[htb-multimaster]] (7), [[htb-sekhmet]] (7), [[htb-sorcery]] (7), [[htb-airtouch]] (6), [[htb-breach]] (6), [[htb-build]] (6), [[htb-cobblestone]] (6), [[htb-era]] (6), [[htb-flight]] (6), [[htb-interpreter]] (6), [[htb-jab]] (6), [[htb-mirage]] (6), [[htb-overflow]] (6), [[htb-phantom]] (6), [[htb-rebound]] (6), [[htb-redelegate]] (6), [[htb-runner]] (6), [[htb-scepter]] (6), [[htb-sherlock-noxious]] (6), [[htb-shibboleth]] (6), [[htb-snapped]] (6), [[htb-tally]] (6), [[htb-tombwatcher]] (6), [[htb-trickster]] (6), [[htb-voleur]] (6), [[htb-active]] (5), [[htb-artificial]] (5), [[htb-cache]] (5), [[htb-checker]] (5), [[htb-codify]] (5), [[htb-cozyhosting]] (5), [[htb-dab]] (5), [[htb-delivery]] (5), [[htb-download]] (5), [[htb-extension]] (5), [[htb-fluffy]] (5), [[htb-formulax]] (5)

_(y 132 mas)_

### john the ripper

3 maquinas.

[[htb-authority]] (1), [[htb-shibboleth]] (1), [[htb-whiterabbit]] (1)

### hydra

28 maquinas.

[[htb-interactive]] (17), [[htb-dab]] (15), [[htb-wall]] (8), [[htb-nineveh]] (7), [[htb-sea]] (7), [[htb-ethereal]] (6), [[htb-fuse]] (6), [[htb-ghoul]] (6), [[htb-mischief]] (6), [[htb-smasher2]] (6), [[htb-teacher]] (6), [[htb-era]] (5), [[htb-fries]] (5), [[htb-luke]] (5), [[htb-playertwo]] (5), [[htb-principal]] (5), [[htb-scavenger]] (5), [[htb-streamio]] (5), [[htb-whiterabbit]] (5), [[htb-admirertoo]] (3), [[htb-cypher]] (2), [[htb-mentor]] (2), [[htb-acute]] (1), [[htb-apocalyst]] (1), [[htb-book]] (1), [[htb-hacknet]] (1), [[htb-sherlock-brutus]] (1), [[htb-trickster]] (1)

### ffuf

131 maquinas.

[[htb-interactive]] (90), [[htb-guardian]] (11), [[htb-interface]] (9), [[htb-solarlab]] (9), [[htb-era]] (8), [[htb-trickster]] (7), [[htb-appsanity]] (6), [[htb-corporate]] (6), [[htb-cybermonday]] (6), [[htb-rainyday]] (6), [[htb-analysis]] (5), [[htb-bagel]] (5), [[htb-hospital]] (5), [[htb-monitorsfour]] (5), [[htb-perfection]] (5), [[htb-pikatwoo]] (5), [[htb-editorial]] (4), [[htb-forgot]] (4), [[htb-kobold]] (4), [[htb-sightless]] (4), [[htb-snoopy]] (4), [[htb-bigbang]] (3), [[htb-bolt]] (3), [[htb-cypher]] (3), [[htb-derailed]] (3), [[htb-down]] (3), [[htb-drive]] (3), [[htb-gofer]] (3), [[htb-heal]] (3), [[htb-mentor]] (3), [[htb-nexus]] (3), [[htb-nocturnal]] (3), [[htb-pollution]] (3), [[htb-runner]] (3), [[htb-silentium]] (3), [[htb-variatype]] (3), [[htb-writer]] (3), [[htb-alert]] (2), [[htb-analytics]] (2), [[htb-blazorized]] (2), [[htb-blurry]] (2), [[htb-boardlight]] (2), [[htb-bruno]] (2), [[htb-clicker]] (2), [[htb-cobblestone]] (2), [[htb-code]] (2), [[htb-darkcorp]] (2), [[htb-devvortex]] (2), [[htb-dump]] (2), [[htb-editor]] (2), [[htb-format]] (2), [[htb-formulax]] (2), [[htb-fries]] (2), [[htb-ghost]] (2), [[htb-headless]] (2), [[htb-helix]] (2), [[htb-intuition]] (2), [[htb-jupiter]] (2), [[htb-lantern]] (2), [[htb-linkvortex]] (2)

_(y 71 mas)_

### gobuster

128 maquinas.

[[htb-interactive]] (76), [[htb-playertwo]] (51), [[htb-oouch]] (25), [[htb-forwardslash]] (17), [[htb-friendzone]] (16), [[htb-admirer]] (15), [[htb-sizzle]] (15), [[htb-bart]] (14), [[htb-patents]] (14), [[htb-vault]] (14), [[htb-book]] (13), [[htb-bighead]] (12), [[htb-charon]] (12), [[htb-dyplesher]] (12), [[htb-ghoul]] (12), [[htb-help]] (12), [[htb-holiday]] (12), [[htb-nineveh]] (12), [[htb-reel2]] (12), [[htb-tartarsauce]] (11), [[htb-registry]] (10), [[htb-arkham]] (9), [[htb-frolic]] (9), [[htb-fuse]] (9), [[htb-hackback]] (9), [[htb-redcross]] (9), [[htb-unattended]] (9), [[htb-chaos]] (8), [[htb-craft]] (8), [[htb-travel]] (8), [[htb-bank]] (7), [[htb-giddy]] (7), [[htb-mantis]] (7), [[htb-player]] (7), [[htb-safe]] (7), [[htb-academy]] (6), [[htb-bankrobber]] (6), [[htb-blunder]] (6), [[htb-bounty]] (6), [[htb-breadcrumbs]] (6), [[htb-buff]] (6), [[htb-cache]] (6), [[htb-calamity]] (6), [[htb-compromised]] (6), [[htb-conceal]] (6), [[htb-cronos]] (6), [[htb-crossfit]] (6), [[htb-grandpa]] (6), [[htb-hawk]] (6), [[htb-joker]] (6), [[htb-laboratory]] (6), [[htb-lazy]] (6), [[htb-luke]] (6), [[htb-magic]] (6), [[htb-nibbles]] (6), [[htb-openadmin]] (6), [[htb-openkeys]] (6), [[htb-ophiuchi]] (6), [[htb-popcorn]] (6), [[htb-proper]] (6)

_(y 68 mas)_

### nmap

534 maquinas.

[[htb-interactive]] (477), [[htb-tentacle]] (92), [[htb-unrested]] (66), [[htb-sherlock-i-like-to]] (65), [[htb-lame-more]] (46), [[htb-reddish]] (41), [[htb-oouch]] (39), [[htb-scriptkiddie]] (37), [[htb-conceal]] (36), [[htb-corporate]] (35), [[htb-conversor]] (34), [[htb-mischief]] (34), [[htb-zetta]] (34), [[htb-vault]] (33), [[htb-airtouch]] (31), [[htb-carrier]] (28), [[htb-olympus]] (28), [[htb-sneaky]] (28), [[htb-static]] (28), [[htb-valentine]] (28), [[htb-ypuffy]] (28), [[htb-cybermonday]] (27), [[htb-oz]] (27), [[htb-trickster]] (27), [[htb-build]] (26), [[htb-ghoul]] (26), [[htb-darkcorp]] (25), [[htb-legacy]] (25), [[htb-talkative]] (25), [[htb-apt]] (24), [[htb-linkvortex]] (24), [[htb-redcross]] (24), [[htb-university]] (24), [[htb-carpediem]] (23), [[htb-cerberus]] (23), [[htb-chatterbox]] (23), [[htb-friendzone]] (23), [[htb-toby]] (22), [[htb-cereal]] (21), [[htb-travel]] (21), [[htb-wifinetictwo]] (21), [[htb-bitlab]] (20), [[htb-devzat]] (20), [[htb-monitorsfour]] (20), [[htb-pilgrimage]] (20), [[htb-shibboleth]] (20), [[htb-beep]] (19), [[htb-blue]] (19), [[htb-expressway]] (19), [[htb-fortune]] (19), [[htb-intelligence]] (19), [[htb-pit]] (19), [[htb-response]] (19), [[htb-scavenger]] (19), [[htb-shocker]] (19), [[htb-underpass]] (19), [[htb-unobtainium]] (19), [[htb-waldo]] (19), [[htb-dyplesher]] (18), [[htb-flujab]] (18)

_(y 474 mas)_

### searchsploit

50 maquinas.

[[htb-interactive]] (34), [[htb-bastard]] (8), [[htb-love]] (7), [[htb-beep]] (6), [[htb-scriptkiddie]] (6), [[htb-buff]] (5), [[htb-help]] (5), [[htb-irked]] (5), [[htb-lame]] (5), [[htb-nineveh]] (5), [[htb-swagshop]] (5), [[htb-valentine]] (5), [[htb-arctic]] (4), [[htb-cache]] (4), [[htb-compromised]] (4), [[htb-hathor]] (4), [[htb-seventeen]] (4), [[htb-solidstate]] (4), [[htb-unbalanced]] (4), [[htb-ambassador]] (3), [[htb-blunder]] (3), [[htb-cronos]] (3), [[htb-grandpa]] (3), [[htb-joker]] (3), [[htb-optimum]] (3), [[htb-passage]] (3), [[htb-player]] (3), [[htb-servmon]] (3), [[htb-traverxec]] (3), [[htb-armageddon]] (2), [[htb-curling]] (2), [[htb-laboratory]] (2), [[htb-lacasadepapel]] (2), [[htb-lame-more]] (2), [[htb-monitors]] (2), [[htb-openadmin]] (2), [[htb-rabbit]] (2), [[htb-registry]] (2), [[htb-scavenger]] (2), [[htb-sense]] (2), [[htb-sink]] (2), [[htb-tally]] (2), [[htb-blocky]] (1), [[htb-doctor]] (1), [[htb-mantis]] (1), [[htb-redcross]] (1), [[htb-reel2]] (1), [[htb-schooled]] (1), [[htb-shoppy]] (1), [[htb-tartarsauce]] (1)

### metasploit

79 maquinas.

[[htb-interactive]] (32), [[htb-lame]] (19), [[htb-scriptkiddie]] (14), [[htb-tabby]] (14), [[htb-arctic]] (12), [[htb-jarmis]] (11), [[htb-lame-more]] (11), [[htb-devel]] (8), [[htb-lacasadepapel]] (8), [[htb-irked]] (7), [[htb-reel]] (7), [[htb-sense]] (7), [[htb-arkham]] (6), [[htb-blue]] (6), [[htb-darkzero]] (6), [[htb-fighter]] (6), [[htb-legacy]] (6), [[htb-postman]] (6), [[htb-silo]] (6), [[chuleta-tunneling]] (6), [[htb-bounty]] (5), [[htb-grandpa]] (5), [[htb-nibbles]] (5), [[htb-sherlock-i-like-to]] (5), [[htb-shibboleth]] (5), [[htb-chatterbox]] (4), [[htb-cronos]] (4), [[htb-frolic]] (4), [[htb-re]] (4), [[htb-reddish]] (4), [[htb-sherlock-logjammer]] (4), [[htb-academy]] (3), [[htb-driver]] (3), [[htb-dropzone]] (3), [[htb-hospital]] (3), [[htb-redelegate]] (3), [[htb-traverxec]] (3), [[htb-ambassador]] (2), [[htb-appsanity]] (2), [[htb-bastard]] (2), [[htb-blunder]] (2), [[htb-buff]] (2), [[htb-ethereal-cor]] (2), [[htb-gofer]] (2), [[htb-granny]] (2), [[htb-mischief-more-root]] (2), [[htb-monitorstwo]] (2), [[htb-orion]] (2), [[htb-passage]] (2), [[htb-pov]] (2), [[htb-redcross]] (2), [[htb-remote]] (2), [[htb-surveillance]] (2), [[htb-acute]] (1), [[htb-antique]] (1), [[htb-backdoor]] (1), [[htb-bart]] (1), [[htb-bastion]] (1), [[htb-cache]] (1), [[htb-cerberus]] (1)

_(y 19 mas)_

### msfvenom

59 maquinas.

[[htb-interactive]] (37), [[htb-rainbow]] (8), [[htb-bighead-bof]] (6), [[htb-hancliffe]] (6), [[htb-legacy]] (6), [[htb-scriptkiddie]] (6), [[htb-buff]] (4), [[htb-chatterbox]] (4), [[htb-giddy]] (4), [[htb-grandpa]] (4), [[htb-logging]] (4), [[htb-reaper]] (4), [[htb-resolute]] (4), [[htb-shibboleth]] (4), [[htb-acute]] (3), [[htb-blue]] (3), [[htb-fighter]] (3), [[htb-hathor]] (3), [[htb-ropetwo]] (3), [[htb-seal]] (3), [[htb-sizzle]] (3), [[htb-tabby]] (3), [[htb-analysis]] (2), [[htb-appsanity]] (2), [[htb-arctic]] (2), [[htb-atom]] (2), [[htb-axlle]] (2), [[htb-backdoor]] (2), [[htb-bruno]] (2), [[htb-compiled]] (2), [[htb-darkzero]] (2), [[htb-driver]] (2), [[htb-faculty]] (2), [[htb-fuse]] (2), [[htb-helpline-kali]] (2), [[htb-hospital]] (2), [[htb-kotarak]] (2), [[htb-logforge]] (2), [[htb-love]] (2), [[htb-playertwo]] (2), [[htb-proper]] (2), [[htb-reel]] (2), [[htb-retired]] (2), [[htb-rustykey]] (2), [[htb-silo]] (2), [[htb-tally]] (2), [[htb-wifinetictwo]] (2), [[htb-bighead]] (1), [[htb-bounty]] (1), [[htb-devel]] (1), [[htb-feline]] (1), [[htb-granny]] (1), [[htb-helpline-win]] (1), [[htb-intuition]] (1), [[htb-jerry]] (1), [[htb-pov]] (1), [[htb-querier]] (1), [[htb-rabbit]] (1), [[htb-university]] (1)

### netexec _(tambien: crackmapexec, nxc)_

142 maquinas.

[[htb-interactive]] (194), [[htb-infiltrator]] (49), [[htb-voleur]] (41), [[htb-vintage]] (38), [[htb-pirate]] (37), [[htb-phantom]] (32), [[htb-mirage]] (30), [[htb-cicada]] (29), [[htb-sendai]] (28), [[htb-rebound]] (27), [[htb-delegate]] (25), [[htb-darkcorp]] (23), [[htb-haze]] (23), [[chuleta-smb-enum]] (23), [[htb-rustykey]] (22), [[htb-administrator]] (21), [[htb-babytwo]] (21), [[htb-tombwatcher]] (21), [[htb-absolute]] (20), [[htb-eighteen]] (20), [[htb-escapetwo]] (20), [[htb-logging]] (20), [[htb-shibuya]] (20), [[htb-breach]] (19), [[htb-puppy]] (19), [[htb-darkzero]] (18), [[htb-scepter]] (18), [[htb-thefrizz]] (18), [[htb-authority]] (17), [[htb-mist]] (17), [[htb-nanocorp]] (17), [[htb-redelegate]] (17), [[htb-baby]] (16), [[htb-retrotwo]] (16), [[htb-slonik]] (16), [[htb-sweep]] (16), [[htb-university]] (16), [[htb-vulncicada]] (16), [[htb-freelancer]] (15), [[htb-fries]] (15), [[htb-retro]] (15), [[htb-bruno]] (14), [[htb-flight]] (14), [[htb-manager]] (14), [[htb-office]] (13), [[htb-overwatch]] (13), [[htb-signed]] (13), [[htb-certified]] (12), [[htb-ghostlink]] (12), [[htb-streamio]] (12), [[htb-jab]] (11), [[htb-search]] (11), [[htb-analysis]] (10), [[htb-axlle]] (10), [[htb-blackfield]] (10), [[htb-cascade]] (10), [[htb-fluffy]] (10), [[htb-certificate]] (9), [[htb-hathor]] (9), [[htb-hospital]] (9)

_(y 82 mas)_

### impacket

97 maquinas.

[[htb-darkcorp]] (50), [[htb-apt]] (26), [[htb-scrambled-linux]] (22), [[htb-darkzero]] (20), [[htb-ghostlink]] (18), [[htb-blue]] (17), [[htb-mist]] (16), [[htb-signed]] (15), [[htb-vintage]] (15), [[htb-infiltrator]] (14), [[htb-rebound]] (14), [[htb-pivotapi]] (13), [[htb-freelancer]] (12), [[htb-retro]] (11), [[htb-ghost]] (10), [[htb-hathor]] (10), [[chuleta-smb-enum]] (10), [[htb-interactive]] (10), [[htb-absolute]] (9), [[htb-pirate]] (9), [[htb-sizzle]] (9), [[htb-flight]] (8), [[htb-retrotwo]] (8), [[htb-rustykey]] (8), [[htb-tally]] (8), [[htb-intelligence]] (7), [[htb-jab]] (7), [[htb-phantom]] (7), [[htb-university]] (7), [[htb-voleur]] (7), [[htb-authority]] (6), [[htb-forest]] (6), [[htb-pivotapi-more]] (6), [[htb-certified]] (5), [[htb-escape]] (5), [[htb-legacy]] (5), [[htb-mantis]] (5), [[htb-mirage]] (5), [[htb-redelegate]] (5), [[htb-sauna]] (5), [[htb-vulncicada]] (5), [[htb-active]] (4), [[htb-breach]] (4), [[htb-bruno]] (4), [[htb-cicada]] (4), [[htb-eighteen]] (4), [[htb-logging]] (4), [[htb-multimaster]] (4), [[htb-outdated]] (4), [[htb-querier]] (4), [[htb-sendai]] (4), [[htb-coder]] (3), [[htb-giddy]] (3), [[htb-haze]] (3), [[htb-manager]] (3), [[htb-omni]] (3), [[htb-puppy]] (3), [[htb-search]] (3), [[htb-vulnescape]] (3), [[htb-acute]] (2)

_(y 37 mas)_

### winpeas

16 maquinas.

[[htb-apt]] (23), [[htb-driver]] (12), [[htb-interactive]] (9), [[htb-optimum]] (7), [[htb-acute]] (5), [[htb-control]] (4), [[htb-sauna]] (4), [[htb-love]] (3), [[htb-hancliffe]] (2), [[htb-analysis]] (1), [[htb-multimaster]] (1), [[htb-pivotapi]] (1), [[htb-proper]] (1), [[htb-re]] (1), [[htb-timelapse]] (1), [[htb-worker]] (1)

### smbmap

38 maquinas.

[[htb-interactive]] (21), [[htb-fuse]] (9), [[htb-active]] (8), [[htb-monteverde]] (6), [[htb-blue]] (5), [[htb-intelligence]] (5), [[htb-search]] (5), [[htb-atom]] (4), [[htb-breadcrumbs]] (4), [[htb-heist]] (4), [[htb-nest]] (4), [[htb-re]] (4), [[htb-sizzle]] (4), [[htb-ypuffy]] (4), [[htb-arkham]] (3), [[htb-bastion]] (3), [[htb-blackfield]] (3), [[htb-cascade]] (3), [[htb-forest]] (3), [[htb-mantis]] (3), [[htb-querier]] (3), [[htb-resolute]] (3), [[htb-writer]] (3), [[htb-driver]] (2), [[htb-friendzone]] (2), [[htb-frolic]] (2), [[htb-lame]] (2), [[htb-legacy]] (2), [[htb-netmon]] (2), [[htb-secnotes]] (2), [[htb-servmon]] (2), [[htb-sharp]] (2), [[chuleta-smb-enum]] (2), [[htb-bankrobber]] (1), [[htb-love]] (1), [[htb-pivotapi]] (1), [[htb-remote]] (1), [[htb-sauna]] (1)

### enum4linux

3 maquinas.

[[htb-active]] (2), [[chuleta-smb-enum]] (2), [[htb-interactive]] (2)


