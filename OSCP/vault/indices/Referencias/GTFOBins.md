# GTFOBins — índice

[[00-inicio|Inicio]] · [[Referencias|Referencias]] · [[GTFOBins|Índice GTFOBins]]

> Fuente: [https://gtfobins.github.io/](https://gtfobins.github.io/) · Licencia: **GPL-3.0** · Espejo local generado desde el repositorio oficial.

GTFOBins — binarios Unix y como abusarlos. Por contexto: sudo, SUID, capabilities.

**458** binarios. Buscá con `Ctrl+O`.

`shell` = obtener shell. `file-read` = leer archivos. `suid`/`sudo` cambian el comando: **mirá la nota del binario**, no copies a ciegas.

| Binario | Funciones |
|---|---|
| [[7z\\|7z]] | file-read |
| [[R\\|R]] | shell |
| [[aa-exec\\|aa-exec]] | shell |
| [[ab\\|ab]] | download, upload |
| [[acr\\|acr]] | command |
| [[agetty\\|agetty]] | shell |
| [[alpine\\|alpine]] | file-read |
| [[ansible-playbook\\|ansible-playbook]] | shell |
| [[ansible-test\\|ansible-test]] | shell |
| [[aoss\\|aoss]] | shell |
| [[apache2\\|apache2]] | file-read |
| [[apache2ctl\\|apache2ctl]] | file-read |
| [[apport-cli\\|apport-cli]] | inherit |
| [[apt-get\\|apt-get]] | inherit, shell |
| [[aptitude\\|aptitude]] | inherit |
| [[ar\\|ar]] | file-read |
| [[arch-nspawn\\|arch-nspawn]] | shell |
| [[aria2c\\|aria2c]] | command, download, file-read |
| [[arj\\|arj]] | file-read, file-write |
| [[arp\\|arp]] | file-read |
| [[as\\|as]] | file-read |
| [[ascii-xfr\\|ascii-xfr]] | file-read |
| [[ascii85\\|ascii85]] | file-read |
| [[ash\\|ash]] | file-write, shell |
| [[aspell\\|aspell]] | file-read |
| [[asterisk\\|asterisk]] | shell |
| [[at\\|at]] | command, shell |
| [[atobm\\|atobm]] | file-read |
| [[autoconf\\|autoconf]] | shell |
| [[autoheader\\|autoheader]] | shell |
| [[autoreconf\\|autoreconf]] | shell |
| [[aws\\|aws]] | file-read, inherit |
| [[base32\\|base32]] | file-read |
| [[base58\\|base58]] | file-read |
| [[base64\\|base64]] | file-read |
| [[basenc\\|basenc]] | file-read |
| [[basez\\|basez]] | file-read |
| [[bash\\|bash]] | download, file-read, file-write, library-load, reverse-shell, shell, upload |
| [[bashbug\\|bashbug]] | inherit |
| [[batcat\\|batcat]] | inherit |
| [[bbot\\|bbot]] | file-read |
| [[bc\\|bc]] | file-read |
| [[bconsole\\|bconsole]] | file-read, shell |
| [[bee\\|bee]] | inherit |
| [[borg\\|borg]] | shell |
| [[bpftrace\\|bpftrace]] | shell |
| [[bridge\\|bridge]] | file-read |
| [[bundle\\|bundle]] | inherit, shell |
| [[busctl\\|busctl]] | inherit, shell |
| [[busybox\\|busybox]] | inherit, reverse-shell, upload |
| [[byebug\\|byebug]] | inherit |
| [[bzip2\\|bzip2]] | file-read |
| [[cabal\\|cabal]] | shell |
| [[cancel\\|cancel]] | upload |
| [[capsh\\|capsh]] | shell |
| [[cargo\\|cargo]] | inherit |
| [[cat\\|cat]] | file-read |
| [[cdist\\|cdist]] | shell |
| [[certbot\\|certbot]] | shell |
| [[chattr\\|chattr]] | privilege-escalation |
| [[check_by_ssh\\|check_by_ssh]] | shell |
| [[check_cups\\|check_cups]] | file-read |
| [[check_log\\|check_log]] | file-read, file-write |
| [[check_memory\\|check_memory]] | file-read |
| [[check_raid\\|check_raid]] | file-read |
| [[check_ssl_cert\\|check_ssl_cert]] | shell |
| [[check_statusfile\\|check_statusfile]] | file-read |
| [[chmod\\|chmod]] | privilege-escalation |
| [[choom\\|choom]] | shell |
| [[chown\\|chown]] | privilege-escalation |
| [[chroot\\|chroot]] | shell |
| [[chrt\\|chrt]] | shell |
| [[clamscan\\|clamscan]] | file-read |
| [[clisp\\|clisp]] | shell |
| [[cmake\\|cmake]] | file-read, shell |
| [[cmp\\|cmp]] | file-read |
| [[cobc\\|cobc]] | shell |
| [[code\\|code]] | download, reverse-shell, upload |
| [[codex\\|codex]] | shell |
| [[column\\|column]] | file-read |
| [[comm\\|comm]] | file-read |
| [[composer\\|composer]] | shell |
| [[cowsay\\|cowsay]] | inherit |
| [[cowthink\\|cowthink]] | inherit |
| [[cp\\|cp]] | file-read, file-write, privilege-escalation |
| [[cpan\\|cpan]] | inherit |
| [[cpio\\|cpio]] | file-read, file-write, shell |
| [[cpulimit\\|cpulimit]] | shell |
| [[crash\\|crash]] | command, inherit |
| [[crontab\\|crontab]] | command, inherit |
| [[csh\\|csh]] | file-write, shell |
| [[csplit\\|csplit]] | file-read, file-write |
| [[csvtool\\|csvtool]] | file-read, file-write, shell |
| [[ctr\\|ctr]] | shell |
| [[cupsfilter\\|cupsfilter]] | file-read |
| [[curl\\|curl]] | download, file-read, file-write, library-load, upload |
| [[cut\\|cut]] | file-read |
| [[dash\\|dash]] | file-write, shell |
| [[date\\|date]] | file-read |
| [[dc\\|dc]] | shell |
| [[dd\\|dd]] | file-read, file-write |
| [[debugfs\\|debugfs]] | shell |
| [[dhclient\\|dhclient]] | shell |
| [[dialog\\|dialog]] | file-read |
| [[diff\\|diff]] | file-read |
| [[dig\\|dig]] | file-read |
| [[distcc\\|distcc]] | shell |
| [[dmesg\\|dmesg]] | file-read, inherit |
| [[dmidecode\\|dmidecode]] | file-write |
| [[dmsetup\\|dmsetup]] | shell |
| [[dnf\\|dnf]] | command |
| [[dnsmasq\\|dnsmasq]] | command |
| [[doas\\|doas]] | shell |
| [[docker\\|docker]] | file-read, file-write, shell |
| [[dos2unix\\|dos2unix]] | file-read, file-write |
| [[dosbox\\|dosbox]] | file-read, file-write |
| [[dotnet\\|dotnet]] | file-read, shell |
| [[dpkg\\|dpkg]] | inherit, shell |
| [[dstat\\|dstat]] | inherit |
| [[dvips\\|dvips]] | shell |
| [[easy_install\\|easy_install]] | inherit |
| [[easyrsa\\|easyrsa]] | shell |
| [[eb\\|eb]] | inherit |
| [[ed\\|ed]] | file-read, file-write, shell |
| [[efax\\|efax]] | file-read |
| [[egrep\\|egrep]] | file-read |
| [[elvish\\|elvish]] | file-read, file-write, shell |
| [[emacs\\|emacs]] | file-read, file-write, shell |
| [[enscript\\|enscript]] | shell |
| [[env\\|env]] | shell |
| [[eqn\\|eqn]] | file-read |
| [[espeak\\|espeak]] | file-read |
| [[ex\\|ex]] | inherit, shell |
| [[exiftool\\|exiftool]] | file-read, file-write, inherit |
| [[expand\\|expand]] | file-read |
| [[expect\\|expect]] | file-read, shell |
| [[facter\\|facter]] | inherit |
| [[fail2ban-client\\|fail2ban-client]] | command |
| [[fastfetch\\|fastfetch]] | command, file-read, shell |
| [[ffmpeg\\|ffmpeg]] | library-load |
| [[fgrep\\|fgrep]] | file-read |
| [[file\\|file]] | file-read |
| [[find\\|find]] | file-read, file-write, shell |
| [[finger\\|finger]] | download, upload |
| [[firejail\\|firejail]] | shell |
| [[fish\\|fish]] | shell |
| [[flock\\|flock]] | shell |
| [[fmt\\|fmt]] | file-read |
| [[fold\\|fold]] | file-read |
| [[forge\\|forge]] | shell |
| [[fping\\|fping]] | file-read |
| [[ftp\\|ftp]] | download, shell, upload |
| [[fzf\\|fzf]] | command, shell |
| [[gawk\\|gawk]] | bind-shell, file-read, file-write, reverse-shell, shell |
| [[gcc\\|gcc]] | file-read, file-write, shell |
| [[gcloud\\|gcloud]] | inherit |
| [[gcore\\|gcore]] | file-read |
| [[gdb\\|gdb]] | file-write, inherit, shell |
| [[gem\\|gem]] | inherit, shell |
| [[genie\\|genie]] | shell |
| [[genisoimage\\|genisoimage]] | file-read |
| [[getent\\|getent]] | privilege-escalation |
| [[ghc\\|ghc]] | shell |
| [[ghci\\|ghci]] | shell |
| [[gimp\\|gimp]] | inherit |
| [[ginsh\\|ginsh]] | shell |
| [[git\\|git]] | file-read, file-write, inherit, shell |
| [[gnuplot\\|gnuplot]] | shell |
| [[go\\|go]] | bind-shell, file-read, file-write, reverse-shell, shell |
| [[grc\\|grc]] | shell |
| [[grep\\|grep]] | file-read |
| [[gtester\\|gtester]] | file-write, shell |
| [[guile\\|guile]] | shell |
| [[gzip\\|gzip]] | file-read |
| [[hashcat\\|hashcat]] | file-write |
| [[head\\|head]] | file-read |
| [[hexdump\\|hexdump]] | file-read |
| [[hg\\|hg]] | shell |
| [[highlight\\|highlight]] | file-read |
| [[hping3\\|hping3]] | shell, upload |
| [[iconv\\|iconv]] | file-read, file-write |
| [[iftop\\|iftop]] | shell |
| [[install\\|install]] | privilege-escalation |
| [[ionice\\|ionice]] | shell |
| [[ip\\|ip]] | file-read, shell |
| [[iptables-save\\|iptables-save]] | file-write |
| [[irb\\|irb]] | inherit |
| [[ispell\\|ispell]] | shell |
| [[java\\|java]] | shell |
| [[jjs\\|jjs]] | download, file-read, file-write, reverse-shell, shell |
| [[joe\\|joe]] | shell |
| [[join\\|join]] | file-read |
| [[journalctl\\|journalctl]] | inherit |
| [[jq\\|jq]] | file-read |
| [[jrunscript\\|jrunscript]] | download, file-read, file-write, reverse-shell, shell |
| [[jshell\\|jshell]] | file-read, file-write, shell |
| [[jtag\\|jtag]] | shell |
| [[julia\\|julia]] | download, file-read, file-write, reverse-shell, shell |
| [[knife\\|knife]] | inherit |
| [[ksshell\\|ksshell]] | file-read |
| [[ksu\\|ksu]] | shell |
| [[kubectl\\|kubectl]] | shell, upload |
| [[last\\|last]] | file-read |
| [[latex\\|latex]] | file-read, file-write, shell |
| [[latexmk\\|latexmk]] | file-read, inherit, shell |
| [[ld.so\\|ld.so]] | shell |
| [[ldconfig\\|ldconfig]] | library-load |
| [[less\\|less]] | command, file-read, file-write, inherit, shell |
| [[lftp\\|lftp]] | shell |
| [[links\\|links]] | file-read |
| [[ln\\|ln]] | privilege-escalation |
| [[loginctl\\|loginctl]] | shell |
| [[logrotate\\|logrotate]] | file-read, file-write, shell |
| [[logsave\\|logsave]] | shell |
| [[look\\|look]] | file-read |
| [[lp\\|lp]] | upload |
| [[ltrace\\|ltrace]] | file-read, file-write, shell |
| [[lua\\|lua]] | bind-shell, download, file-read, file-write, reverse-shell, shell, upload |
| [[lualatex\\|lualatex]] | inherit |
| [[luatex\\|luatex]] | inherit |
| [[lwp-download\\|lwp-download]] | download, file-read, file-write |
| [[lwp-request\\|lwp-request]] | file-read |
| [[lxd\\|lxd]] | shell |
| [[m4\\|m4]] | command, file-read, shell |
| [[mail\\|mail]] | shell |
| [[make\\|make]] | file-read, file-write, shell |
| [[man\\|man]] | file-read, inherit, shell |
| [[mawk\\|mawk]] | file-read, file-write, shell |
| [[minicom\\|minicom]] | shell |
| [[more\\|more]] | file-read, shell |
| [[mosh-server\\|mosh-server]] | shell |
| [[mosquitto\\|mosquitto]] | file-read |
| [[mount\\|mount]] | privilege-escalation |
| [[msfconsole\\|msfconsole]] | inherit |
| [[msgattrib\\|msgattrib]] | file-read |
| [[msgcat\\|msgcat]] | file-read |
| [[msgconv\\|msgconv]] | file-read |
| [[msgfilter\\|msgfilter]] | file-read, shell |
| [[msgmerge\\|msgmerge]] | file-read |
| [[msguniq\\|msguniq]] | file-read |
| [[mtr\\|mtr]] | file-read |
| [[multitime\\|multitime]] | shell |
| [[mutt\\|mutt]] | file-read |
| [[mv\\|mv]] | file-write, privilege-escalation |
| [[mypy\\|mypy]] | file-read, file-write |
| [[mysql\\|mysql]] | library-load, shell |
| [[nano\\|nano]] | file-read, file-write, shell |
| [[nasm\\|nasm]] | file-read |
| [[nc\\|nc]] | bind-shell, download, reverse-shell, upload |
| [[ncdu\\|ncdu]] | shell |
| [[ncftp\\|ncftp]] | shell |
| [[needrestart\\|needrestart]] | inherit |
| [[neofetch\\|neofetch]] | file-read, shell |
| [[nft\\|nft]] | file-read |
| [[nginx\\|nginx]] | download, library-load, upload |
| [[nice\\|nice]] | shell |
| [[nl\\|nl]] | file-read |
| [[nm\\|nm]] | file-read |
| [[nmap\\|nmap]] | file-read, file-write, inherit, shell |
| [[node\\|node]] | bind-shell, download, file-read, file-write, reverse-shell, shell, upload |
| [[nohup\\|nohup]] | command, shell |
| [[npm\\|npm]] | shell |
| [[nroff\\|nroff]] | file-read, shell |
| [[nsenter\\|nsenter]] | shell |
| [[ntpdate\\|ntpdate]] | file-read |
| [[octave\\|octave]] | file-read, file-write, shell |
| [[od\\|od]] | file-read |
| [[opencode\\|opencode]] | command, inherit |
| [[openssl\\|openssl]] | download, file-read, file-write, library-load, reverse-shell, upload |
| [[openvpn\\|openvpn]] | file-read, shell |
| [[openvt\\|openvt]] | command |
| [[opkg\\|opkg]] | shell |
| [[pandoc\\|pandoc]] | file-read, file-write, inherit |
| [[passwd\\|passwd]] | privilege-escalation |
| [[paste\\|paste]] | file-read |
| [[pax\\|pax]] | file-read |
| [[pdb\\|pdb]] | inherit |
| [[pdflatex\\|pdflatex]] | file-read, file-write, shell |
| [[pdftex\\|pdftex]] | shell |
| [[perf\\|perf]] | shell |
| [[perl\\|perl]] | download, file-read, reverse-shell, shell, upload |
| [[perlbug\\|perlbug]] | shell |
| [[pexec\\|pexec]] | shell |
| [[pg\\|pg]] | file-read, shell |
| [[php\\|php]] | command, download, file-read, file-write, reverse-shell, shell, upload |
| [[pic\\|pic]] | file-read, shell |
| [[pidstat\\|pidstat]] | shell |
| [[pip\\|pip]] | inherit, shell |
| [[pipx\\|pipx]] | inherit |
| [[pkexec\\|pkexec]] | shell |
| [[pkg\\|pkg]] | command |
| [[plymouth\\|plymouth]] | shell |
| [[podman\\|podman]] | shell |
| [[poetry\\|poetry]] | inherit |
| [[posh\\|posh]] | shell |
| [[pr\\|pr]] | file-read |
| [[procmail\\|procmail]] | command |
| [[pry\\|pry]] | inherit |
| [[psftp\\|psftp]] | shell |
| [[psql\\|psql]] | inherit, shell |
| [[ptx\\|ptx]] | file-read |
| [[puppet\\|puppet]] | file-read, file-write, shell |
| [[pwsh\\|pwsh]] | file-write, shell |
| [[pygmentize\\|pygmentize]] | file-read |
| [[pyright\\|pyright]] | file-read |
| [[python\\|python]] | download, file-read, file-write, library-load, reverse-shell, shell, upload |
| [[qpdf\\|qpdf]] | file-read |
| [[rake\\|rake]] | file-read, inherit |
| [[ranger\\|ranger]] | shell |
| [[rc\\|rc]] | shell |
| [[readelf\\|readelf]] | file-read |
| [[redcarpet\\|redcarpet]] | file-read |
| [[redis\\|redis]] | file-write |
| [[restic\\|restic]] | command, shell, upload |
| [[rev\\|rev]] | file-read |
| [[rlogin\\|rlogin]] | upload |
| [[rlwrap\\|rlwrap]] | file-write, shell |
| [[rpm\\|rpm]] | command, inherit, shell |
| [[rpmdb\\|rpmdb]] | inherit, shell |
| [[rpmquery\\|rpmquery]] | inherit, shell |
| [[rpmverify\\|rpmverify]] | inherit, shell |
| [[rsync\\|rsync]] | shell |
| [[rsyslogd\\|rsyslogd]] | command |
| [[rtorrent\\|rtorrent]] | shell |
| [[ruby\\|ruby]] | download, file-read, file-write, library-load, reverse-shell, shell, upload |
| [[run-mailcap\\|run-mailcap]] | inherit |
| [[run-parts\\|run-parts]] | shell |
| [[runscript\\|runscript]] | shell |
| [[rustc\\|rustc]] | file-read, file-write, inherit |
| [[rustdoc\\|rustdoc]] | file-read, file-write |
| [[rustfmt\\|rustfmt]] | file-read |
| [[rustup\\|rustup]] | command, shell |
| [[sash\\|sash]] | shell |
| [[scanmem\\|scanmem]] | shell |
| [[scp\\|scp]] | download, shell, upload |
| [[screen\\|screen]] | file-write, shell |
| [[script\\|script]] | file-write, shell |
| [[scrot\\|scrot]] | shell |
| [[sed\\|sed]] | file-read, file-write, shell |
| [[service\\|service]] | shell |
| [[setarch\\|setarch]] | shell |
| [[setcap\\|setcap]] | privilege-escalation |
| [[setfacl\\|setfacl]] | privilege-escalation |
| [[setlock\\|setlock]] | shell |
| [[sftp\\|sftp]] | download, shell, upload |
| [[sg\\|sg]] | shell |
| [[shred\\|shred]] | file-write |
| [[shuf\\|shuf]] | file-read, file-write |
| [[slsh\\|slsh]] | shell |
| [[smbclient\\|smbclient]] | download, shell, upload |
| [[snap\\|snap]] | command |
| [[socat\\|socat]] | bind-shell, download, file-read, file-write, reverse-shell, shell, upload |
| [[socket\\|socket]] | bind-shell, reverse-shell |
| [[soelim\\|soelim]] | file-read |
| [[softlimit\\|softlimit]] | shell |
| [[sort\\|sort]] | file-read, file-write |
| [[split\\|split]] | file-read, file-write, shell |
| [[sqlite3\\|sqlite3]] | file-read, file-write, shell |
| [[sqlmap\\|sqlmap]] | inherit |
| [[ss\\|ss]] | file-read |
| [[ssh\\|ssh]] | download, file-read, shell, upload |
| [[ssh-agent\\|ssh-agent]] | shell |
| [[ssh-copy-id\\|ssh-copy-id]] | file-read, file-write |
| [[ssh-keygen\\|ssh-keygen]] | library-load |
| [[ssh-keyscan\\|ssh-keyscan]] | file-read |
| [[sshfs\\|sshfs]] | command, download, shell, upload |
| [[sshpass\\|sshpass]] | shell |
| [[sshuttle\\|sshuttle]] | shell |
| [[start-stop-daemon\\|start-stop-daemon]] | shell |
| [[stdbuf\\|stdbuf]] | shell |
| [[strace\\|strace]] | file-write, shell |
| [[strings\\|strings]] | file-read |
| [[su\\|su]] | shell |
| [[sudo\\|sudo]] | shell |
| [[sysctl\\|sysctl]] | command, file-read |
| [[systemctl\\|systemctl]] | inherit, shell |
| [[systemd-resolve\\|systemd-resolve]] | inherit |
| [[systemd-run\\|systemd-run]] | command, shell |
| [[tac\\|tac]] | file-read |
| [[tail\\|tail]] | file-read |
| [[tailscale\\|tailscale]] | upload |
| [[tar\\|tar]] | download, file-read, file-write, shell, upload |
| [[task\\|task]] | shell |
| [[taskset\\|taskset]] | shell |
| [[tasksh\\|tasksh]] | shell |
| [[tbl\\|tbl]] | file-read |
| [[tclsh\\|tclsh]] | library-load, reverse-shell, shell |
| [[tcpdump\\|tcpdump]] | command, file-write |
| [[tcsh\\|tcsh]] | file-write, shell |
| [[tdbtool\\|tdbtool]] | shell |
| [[tee\\|tee]] | file-write |
| [[telnet\\|telnet]] | reverse-shell, shell |
| [[terraform\\|terraform]] | file-read |
| [[tex\\|tex]] | shell |
| [[tftp\\|tftp]] | download, upload |
| [[tic\\|tic]] | file-read |
| [[time\\|time]] | shell |
| [[timedatectl\\|timedatectl]] | inherit |
| [[timeout\\|timeout]] | shell |
| [[tmate\\|tmate]] | shell |
| [[tmux\\|tmux]] | file-read, shell |
| [[top\\|top]] | shell |
| [[torify\\|torify]] | shell |
| [[torsocks\\|torsocks]] | shell |
| [[troff\\|troff]] | file-read |
| [[tsc\\|tsc]] | file-read, file-write |
| [[tshark\\|tshark]] | inherit |
| [[ul\\|ul]] | file-read |
| [[unexpand\\|unexpand]] | file-read |
| [[uniq\\|uniq]] | file-read |
| [[unshare\\|unshare]] | shell |
| [[unsquashfs\\|unsquashfs]] | privilege-escalation |
| [[unzip\\|unzip]] | privilege-escalation |
| [[update-alternatives\\|update-alternatives]] | file-write |
| [[urlget\\|urlget]] | file-read |
| [[uuencode\\|uuencode]] | file-read |
| [[uv\\|uv]] | shell |
| [[vagrant\\|vagrant]] | inherit |
| [[valgrind\\|valgrind]] | shell |
| [[varnishncsa\\|varnishncsa]] | file-write |
| [[vi\\|vi]] | file-read, file-write, shell |
| [[vigr\\|vigr]] | inherit |
| [[vim\\|vim]] | file-read, inherit |
| [[vipw\\|vipw]] | inherit |
| [[virsh\\|virsh]] | command, file-write |
| [[volatility\\|volatility]] | inherit |
| [[w3m\\|w3m]] | file-read |
| [[wall\\|wall]] | file-read |
| [[watch\\|watch]] | shell |
| [[wc\\|wc]] | file-read |
| [[wg-quick\\|wg-quick]] | shell |
| [[wget\\|wget]] | download, file-read, file-write, shell, upload |
| [[whiptail\\|whiptail]] | file-read |
| [[whois\\|whois]] | download, upload |
| [[wireshark\\|wireshark]] | file-write, inherit |
| [[wish\\|wish]] | inherit |
| [[xargs\\|xargs]] | file-read, shell |
| [[xdg-user-dir\\|xdg-user-dir]] | shell |
| [[xdotool\\|xdotool]] | shell |
| [[xmodmap\\|xmodmap]] | file-read |
| [[xmore\\|xmore]] | file-read |
| [[xpad\\|xpad]] | file-read |
| [[xxd\\|xxd]] | file-read, file-write |
| [[xz\\|xz]] | file-read |
| [[yarn\\|yarn]] | shell |
| [[yash\\|yash]] | shell |
| [[yelp\\|yelp]] | file-read |
| [[yt-dlp\\|yt-dlp]] | shell |
| [[yum\\|yum]] | command, download, inherit |
| [[zathura\\|zathura]] | shell |
| [[zcat\\|zcat]] | file-read |
| [[zgrep\\|zgrep]] | file-read |
| [[zic\\|zic]] | command |
| [[zip\\|zip]] | file-read, shell |
| [[zless\\|zless]] | inherit |
| [[zsh\\|zsh]] | download, file-read, file-write, inherit, reverse-shell, shell, upload |
| [[zsoelim\\|zsoelim]] | file-read |
| [[zypper\\|zypper]] | shell |
