## This only builds the userland portion, kernel modules are excluded.
## Support for distros older than EL7 is dropped.

#define afsvers 1.8.0pre5
%define afsvers 1.8.3
%define pkgvers 1.8.3
# for beta/rc releases make pkgrel 0.<tag>
# for real releases make pkgrel 1 (or more for extra releases)
#define pkgrel 0.pre1
%define pkgrel 1.0.kth.7

Summary: A distributed filesystem
Name: openafs
Version: %{pkgvers}
Release: %{pkgrel}%{?dist}
License: IBM Public License
URL: https://www.openafs.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-root
Group: Networking/Filesystems
BuildRequires: ncurses-devel, flex, bison, automake, autoconf, libtool
BuildRequires: systemd-units
BuildRequires: perl-devel
BuildRequires: perl(ExtUtils::Embed)
BuildRequires: krb5-devel

# TODO is this relevant for a server-only build?
ExclusiveArch: %{ix86} x86_64 ia64 s390 s390x sparc64 ppc ppc64

#    http://dl.openafs.org/dl/openafs/candidate/(afsvers)/...
Source0: https://openafs.org/dl/openafs/%{afsvers}/openafs-%{afsvers}-src.tar.bz2
Source1: https://openafs.org/dl/openafs/%{afsvers}/openafs-%{afsvers}-doc.tar.bz2
%define srcdir openafs-%{afsvers}

Source10: https://www.openafs.org/dl/openafs/%{afsvers}/RELNOTES-%{afsvers}
Source11: https://www.openafs.org/dl/openafs/%{afsvers}/ChangeLog
Source20: https://www.central.org/dl/cellservdb/CellServDB.2018-05-14
# firewalld service devinitions
Source21: afs3-bos.xml
Source23: afs3-fileserver.xml
Source24: afs3-prserver.xml
Source26: afs3-update.xml
Source27: afs3-vlserver.xml
Source28: afs3-volser.xml

%description
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides common files shared across all the various
OpenAFS packages but are not necessarily tied to a client or server.


%package server
Requires: openafs = %{version}
Summary: OpenAFS Filesystem Server
Group: Networking/Filesystems
Requires: systemd-units
Requires(post): systemd-units, systemd-sysv
Requires(preun): systemd-units
Requires(postun): systemd-units

%description server
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides basic server support to host files in an AFS
Cell.

%package authlibs
Summary: OpenAFS authentication shared libraries
Group: Networking/Filesystems

%description authlibs
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides a shared version of libafsrpc and libafsauthent. 
None of the programs included with OpenAFS currently use these shared 
libraries; however, third-party software that wishes to perform AFS 
authentication may link against them.

%package authlibs-devel
Requires: openafs-authlibs = %{version}-%{release}
Requires: openafs-devel = %{version}-%{release}
Summary: OpenAFS shared library development
Group: Development/Filesystems

%description authlibs-devel
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package includes the static versions of libafsrpc and 
libafsauthent, and symlinks required for building against the dynamic 
libraries.

%package devel
Summary: OpenAFS Development Libraries and Headers
Group: Development/Filesystems
Requires: openafs = %{version}-%{release}

%description devel
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides static development libraries and headers needed
to compile AFS applications.  Note: AFS currently does not provide
shared libraries.

%package docs
Summary: OpenAFS user and administrator documentation
Requires: openafs = %{version}-%{release}
Group: Networking/Filesystems

%description docs
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides HTML documentation for OpenAFS users and system
administrators.

%package krb5
Summary: OpenAFS programs to use with krb5
Requires: openafs = %{version}
Group: Networking/Filesystems
BuildRequires: krb5-devel

%description krb5
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides compatibility programs so you can use krb5
to authenticate to AFS services, instead of using the AFS homegrown
krb4 lookalike services.

%package server-firewalld
Summary: OpenAFS server firewalld configuration for a server
Requires: openafs = %{version}, openafs-server = %{version}, firewalld-filesystem
Requires(post): firewalld-filesystem
Group: Networking/Filesystems

%description server-firewalld
The AFS distributed filesystem.  AFS is a distributed filesystem
allowing cross-platform sharing of files among multiple computers.
Facilities are provided for access control, authentication, backup and
administrative management.

This package provides the service definitions to use in a firewalld
setup for an OpenAFS server.


##############################################################################
#
# PREP
#
##############################################################################

%prep
# Install OpenAFS src and doc
%setup -q -b 1 -n %{srcdir}

##############################################################################
#
# building
#
##############################################################################
%build
kv='26'
case %{_arch} in
    x86_64)                         sysname=amd64_linux${kv}        ;;
    alpha*)                         sysname=alpha_linux_${kv}       ;;
    i386|i486|i586|i686|athlon)     sysname=i386_linux${kv}         ;;
    *)                              sysname=%{_arch}_linux${kv}     ;;
esac
DESTDIR=$RPM_BUILD_ROOT; export DESTDIR
CFLAGS="$RPM_OPT_FLAGS"; export CFLAGS

KRB5_CONFIG="%{krb5config}"
export KRB5_CONFIG

#if [[ ! -f configure ]]; then
    echo %{afsvers} > .version
    sh regen.sh
#fi

# Fedora 23+ won't compile with the redhat-hardened-ld
%if 0%{?fedora} >= 23
LDFLAGS=$( echo %__global_ldflags | sed 's!-specs=/usr/lib/rpm/redhat/redhat-hardened-ld!!'); export LDFLAGS
%endif

%configure \
    --with-afs-sysname=${sysname} \
    --disable-strip-binaries \
    --disable-kernel-module \
    --enable-debug \
    --with-krb5 \
    --enable-bitmap-later \
    --enable-supergroups \
    || exit 1

make
#make -j16

##############################################################################
#
# installation
#
##############################################################################
%install
make install DESTDIR=$RPM_BUILD_ROOT
export DONT_GPRINTIFY=1

kv='26'

case %{_arch} in
    x86_64)                         sysname=amd64_linux${kv}        ;;
    alpha*)                         sysname=alpha_linux_${kv}       ;;
    i386|i486|i586|i686|athlon)     sysname=i386_linux${kv}         ;;
    *)                              sysname=%{_arch}_linux${kv}     ;;
esac

# Copy root.client config files
mkdir -p $RPM_BUILD_ROOT/etc/openafs
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -m 644 src/packaging/RedHat/openafs-server.service $RPM_BUILD_ROOT%{_unitdir}/openafs-server.service


#
# Install DOCUMENTATION
#

# Build the DOC directory
mkdir -p $RPM_BUILD_ROOT/$RPM_DOC_DIR/openafs-%{afsvers}
tar cf - -C doc LICENSE html pdf | \
    tar xf - -C $RPM_BUILD_ROOT/$RPM_DOC_DIR/openafs-%{afsvers}
install -m 644 %{SOURCE10} $RPM_BUILD_ROOT/$RPM_DOC_DIR/openafs-%{afsvers}
install -m 644 %{SOURCE11} $RPM_BUILD_ROOT/$RPM_DOC_DIR/openafs-%{afsvers}

# remove unused man pages
for x in afs_ftpd afs_inetd afs_login afs_rcp afs_rlogind afs_rsh \
    dkload knfs symlink symlink_list symlink_make \
    symlink_remove; do
        rm -f $RPM_BUILD_ROOT%{_mandir}/man1/${x}.1
done

#
# create filelist
#
grep -v "^#" >openafs-file-list <<EOF-openafs-file-list
%{_bindir}/afsmonitor
%{_bindir}/bos
%{_bindir}/fs
%{_bindir}/pagsh
%{_bindir}/pagsh.krb
%{_bindir}/pts
%{_bindir}/restorevol
%{_bindir}/scout
%{_bindir}/sys
%{_bindir}/tokens
%{_bindir}/tokens.krb
%{_bindir}/translate_et
%{_bindir}/xstat_cm_test
%{_bindir}/xstat_fs_test
%{_bindir}/udebug
%{_bindir}/unlog
%{_sbindir}/backup
%{_sbindir}/butc
%{_sbindir}/fms
%{_sbindir}/fstrace
%{_sbindir}/read_tape
%{_sbindir}/rxdebug
%{_sbindir}/uss
%{_sbindir}/vos
%{_sbindir}/vsys
EOF-openafs-file-list

# add man pages to the list
cat openafs-man1files \
    | ( while read x; do echo "%{_mandir}/man1/$x"; done ) \
    >>openafs-file-list
cat openafs-man5files \
    | ( while read x; do echo "%{_mandir}/man5/$x"; done ) \
    >>openafs-file-list
cat openafs-man8files \
    | ( while read x; do echo "%{_mandir}/man8/$x"; done ) \
    >>openafs-file-list

#
# Remove files we're not installing
#

# the rest are not needed.
for f in dlog dpass install knfs livesys ; do
    rm -f $RPM_BUILD_ROOT%{_bindir}/$f
done

# not supported on Linux or duplicated
for f in kdb rmtsysd kpwvalid ; do
    rm -f $RPM_BUILD_ROOT%{_sbindir}/$f
done

# remove man pages from programs deleted above
for f in 1/dlog 1/copyauth 1/dpass 1/livesys 8/rmtsysd 8/aklog_dynamic_auth 8/kdb 8/kpwvalid 8/xfs_size_check 1/package_test 5/package 8/package ; do
    rm -f $RPM_BUILD_ROOT%{_mandir}/man$f.*
done

#delete static libraries not in upstream package
rm -f $RPM_BUILD_ROOT%{_libdir}/libjuafs.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libuafs.a

# Populate /etc/openafs/server
## Create empty files to be configured later
mkdir $RPM_BUILD_ROOT%{_sysconfdir}/openafs/server
touch $RPM_BUILD_ROOT%{_sysconfdir}/openafs/server/CellServDB
touch $RPM_BUILD_ROOT%{_sysconfdir}/openafs/server/ThisCell
touch $RPM_BUILD_ROOT%{_sysconfdir}/openafs/server/krb.conf
touch $RPM_BUILD_ROOT%{_sysconfdir}/openafs/server/UserList


# Fix systemd service unit which has transarc paths
## Fix location of environment file
sed -i 's!EnvironmentFile=-/etc/sysconfig/openafs!EnvironmentFile=-%{_sysconfdir}/sysconfig/openafs-server!g' $RPM_BUILD_ROOT%{_unitdir}/openafs-server.service
## Fix location of bosserver
sed -i 's!/usr/afs/bin/bosserver!%{_sbindir}/bosserver!' $RPM_BUILD_ROOT%{_unitdir}/openafs-server.service

# Set the executable bit on libraries in libdir, so rpmbuild knows to
# create "Provides" entries in the package metadata for the libraries
chmod +x $RPM_BUILD_ROOT%{_libdir}/*.so*

# Set up firewalld files
# (rpmlint warns, but macro usage here matches firewalld.spec)
install -d -m 755 %{buildroot}%{_prefix}/lib/firewalld/services
install -p -m 644 %SOURCE21 %{buildroot}%{_prefix}/lib/firewalld/services/afs3-bos.xml
install -p -m 644 %SOURCE23 %{buildroot}%{_prefix}/lib/firewalld/services/afs3-fileserver.xml
install -p -m 644 %SOURCE24 %{buildroot}%{_prefix}/lib/firewalld/services/afs3-prserver.xml
install -p -m 644 %SOURCE26 %{buildroot}%{_prefix}/lib/firewalld/services/afs3-update.xml
install -p -m 644 %SOURCE27 %{buildroot}%{_prefix}/lib/firewalld/services/afs3-vlserver.xml
install -p -m 644 %SOURCE28 %{buildroot}%{_prefix}/lib/firewalld/services/afs3-volser.xml

# Remove client related files
rm -f $RPM_BUILD_ROOT%{_sysconfdir}/openafs/CellServDB
rm -f $RPM_BUILD_ROOT%{_bindir}/afsio
rm -f $RPM_BUILD_ROOT%{_bindir}/cmdebug
rm -f $RPM_BUILD_ROOT%{_bindir}/up
rm -f $RPM_BUILD_ROOT%{_sbindir}/afsd
rm -f $RPM_BUILD_ROOT%{_prefix}/share/openafs/C/afszcm.cat
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/cmdebug.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/up.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/afs.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/afs_cache.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/afs_volume_header.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/afszcm.cat.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/cacheinfo.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/afsd.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man8/vsys.*
rm -f $RPM_BUILD_ROOT%{_mandir}/man5/CellAlias.*


##############################################################################
###
### clean
###
##############################################################################
%clean
rm -f openafs-file-list
[ "$RPM_BUILD_ROOT" != "/" -a "x%{debugspec}" != "x1" ] && \
    rm -fr $RPM_BUILD_ROOT

##############################################################################
###
### scripts
###
##############################################################################
%post authlibs -p /sbin/ldconfig

%postun authlibs -p /sbin/ldconfig

%preun server
if [ $1 -eq 0 ] ; then
    /bin/systemctl --no-reload disable openafs-server.service > /dev/null 2>&1 || :
    /bin/systemctl stop openafs-server.service > /dev/null 2>&1 || :
fi

%postun server
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

##############################################################################
###
### file lists
###
##############################################################################
%files 
#-f openafs-file-list
%defattr(-,root,root)
%{_bindir}/afsmonitor
%{_bindir}/bos
%{_bindir}/fs
%{_bindir}/pagsh
%{_bindir}/pagsh.krb
%{_bindir}/pts
%{_bindir}/restorevol
%{_bindir}/scout
%{_bindir}/sys
%{_bindir}/tokens
%{_bindir}/tokens.krb
%{_bindir}/translate_et
%{_bindir}/xstat_cm_test
%{_bindir}/xstat_fs_test
%{_bindir}/udebug
%{_bindir}/unlog
%{_sbindir}/backup
%{_sbindir}/butc
%{_sbindir}/fms
%{_sbindir}/fstrace
%{_sbindir}/read_tape
%{_sbindir}/rxdebug
%{_sbindir}/uss
%{_sbindir}/vos
%{_sbindir}/vsys
%{_libdir}/librokenafs.so.*
%{_libdir}/libafshcrypto.so.*
%{_mandir}/man1/fs*.gz
%{_mandir}/man1/pts*.gz
%{_mandir}/man1/vos*.gz
%{_mandir}/man1/afs.1.gz
%{_mandir}/man1/afsmonitor.1.gz
%{_mandir}/man1/pagsh.1.gz
%{_mandir}/man1/pagsh.krb.1.gz
%{_mandir}/man1/rxdebug.1.gz
%{_mandir}/man1/restorevol.1.gz
%{_mandir}/man1/scout.1.gz
%{_mandir}/man1/tokens.1.gz
%{_mandir}/man1/tokens.krb.1.gz
%{_mandir}/man1/translate_et.1.gz
%{_mandir}/man1/xstat_cm_test.1.gz
%{_mandir}/man1/xstat_fs_test.1.gz
%{_mandir}/man5/afsmonitor.5.gz
%{_mandir}/man1/udebug.1.gz
%{_mandir}/man1/unlog.1.gz
%{_mandir}/man5/uss.5.gz
%{_mandir}/man5/uss_bulk.5.gz
%{_mandir}/man8/bos*
%{_mandir}/man8/fstrace*
%{_mandir}/man1/sys.1.gz
%{_mandir}/man8/backup*
%{_mandir}/man5/butc.5.gz
%{_mandir}/man5/butc_logs.5.gz
%{_mandir}/man8/butc.8.gz
%{_mandir}/man8/fms.8.gz
%{_mandir}/man8/read_tape.8.gz
%{_mandir}/man8/fssync-debug*
%{_mandir}/man8/uss*
%{_mandir}/man5/CellServDB.5.gz
%{_mandir}/man5/ThisCell.5.gz
%doc %{_docdir}/openafs-%{afsvers}/LICENSE

%files docs
%defattr(-,root,root)
%docdir %{_docdir}/openafs-%{afsvers}
%dir %{_docdir}/openafs-%{afsvers}
%{_docdir}/openafs-%{afsvers}/ChangeLog
%{_docdir}/openafs-%{afsvers}/RELNOTES-%{afsvers}
%{_docdir}/openafs-%{afsvers}/pdf

%files server
%defattr(-,root,root)
%dir %{_sysconfdir}/openafs/server
%config(noreplace) %{_sysconfdir}/openafs/server/CellServDB
%config(noreplace) %{_sysconfdir}/openafs/server/ThisCell
%config(noreplace) %{_sysconfdir}/openafs/server/UserList
%config(noreplace) %{_sysconfdir}/openafs/server/krb.conf
%ghost %config(noreplace) %{_sysconfdir}/openafs/BosConfig
%ghost %config(noreplace) %{_sysconfdir}/openafs/server/rxkad.keytab
%ghost %config(noreplace) %{_sysconfdir}/sysconfig/openafs-server
%{_bindir}/akeyconvert
%{_sbindir}/bosserver
%{_sbindir}/bos_util
%{_libexecdir}/openafs/buserver
%{_libexecdir}/openafs/dafileserver
%{_sbindir}/dafssync-debug
%{_libexecdir}/openafs/dasalvager
%{_libexecdir}/openafs/davolserver
%{_libexecdir}/openafs/fileserver
%{_sbindir}/fssync-debug
%{_sbindir}/pt_util
%{_libexecdir}/openafs/ptserver
%{_libexecdir}/openafs/salvager
%{_libexecdir}/openafs/salvageserver
%{_sbindir}/salvsync-debug
%{_sbindir}/state_analyzer
%{_libexecdir}/openafs/upclient
%{_libexecdir}/openafs/upserver
%{_libexecdir}/openafs/vlserver
%{_sbindir}/volinfo
%{_libexecdir}/openafs/volserver
%{_sbindir}/prdb_check
%{_sbindir}/vldb_check
%{_sbindir}/vldb_convert
%{_sbindir}/voldump
%{_sbindir}/volscan
%{_unitdir}/openafs-server.service
%{_mandir}/man3/AFS::ukernel.*
%{_mandir}/man5/AuthLog.*
%{_mandir}/man5/BackupLog.*
%{_mandir}/man5/BosConfig.*
%{_mandir}/man5/BosLog.*
%{_mandir}/man5/FORCESALVAGE.*
%{_mandir}/man5/FileLog.*
%{_mandir}/man5/KeyFile.*
%{_mandir}/man5/KeyFileExt.*
%{_mandir}/man5/NetInfo.*
%{_mandir}/man5/NetRestrict.*
%{_mandir}/man5/NoAuth.*
%{_mandir}/man5/PtLog.*
%{_mandir}/man5/SALVAGE.fs.*
%{_mandir}/man5/SalvageLog.*
%{_mandir}/man5/sysid.*
%{_mandir}/man5/UserList.*
%{_mandir}/man5/VLLog.*
%{_mandir}/man5/VolserLog.*
%{_mandir}/man5/bdb.DB0.*
%{_mandir}/man5/fms.log.*
%{_mandir}/man5/krb.conf.*
%{_mandir}/man5/krb.excl.*
%{_mandir}/man5/prdb.DB0.*
%{_mandir}/man5/salvage.lock.*
%{_mandir}/man5/tapeconfig.*
%{_mandir}/man5/vldb.DB0.*
%{_mandir}/man8/akeyconvert.*
%{_mandir}/man8/buserver.*
%{_mandir}/man8/fileserver.*
%{_mandir}/man8/dafileserver.*
%{_mandir}/man8/dafssync-debug*
%{_mandir}/man8/dasalvager.*
%{_mandir}/man8/davolserver.*
%{_mandir}/man8/prdb_check.*
%{_mandir}/man8/ptserver.*
%{_mandir}/man8/pt_util.*
%{_mandir}/man8/salvager.*
%{_mandir}/man8/salvageserver.*
%{_mandir}/man8/state_analyzer.*
%{_mandir}/man8/upclient.*
%{_mandir}/man8/upserver.*
%{_mandir}/man8/vldb_check.*
%{_mandir}/man8/vldb_convert.*
%{_mandir}/man8/vlserver.*
%{_mandir}/man8/voldump.*
%{_mandir}/man8/volinfo.*
%{_mandir}/man8/volscan.*
%{_mandir}/man8/volserver.*

%files authlibs
%defattr(-,root,root)
%{_libdir}/libafsauthent.so.*
%{_libdir}/libafsrpc.so.*
%{_libdir}/libkopenafs.so.*

%files authlibs-devel
%defattr(-,root,root)
%{_includedir}/kopenafs.h
%{_libdir}/libafsauthent.a
%{_libdir}/libafscp.a
%{_libdir}/libafsrpc.a
%{_libdir}/libafsauthent_pic.a
%{_libdir}/libafsrpc_pic.a
%{_libdir}/libkopenafs.a
%{_libdir}/libafsauthent.so
%{_libdir}/libafsrpc.so
%{_libdir}/libkopenafs.so

%files devel
%defattr(-,root,root)
%{_bindir}/afs_compile_et
%{_bindir}/rxgen
%{_includedir}/afs
%{_includedir}/lock.h
%{_includedir}/lwp.h
%{_includedir}/rx
%{_includedir}/timer.h
%{_includedir}/ubik.h
%{_includedir}/ubik_int.h
%{_includedir}/opr/queue.h
%{_includedir}/opr/lock.h
%{_libdir}/afs
%{_libdir}/liblwp.a
%{_libdir}/libopr.a
%{_libdir}/librx.a
%{_libdir}/librxkad.a
%{_libdir}/librxstat.a
%{_libdir}/libubik.a
%{_libdir}/librokenafs.a
%{_libdir}/librokenafs.so
%{_libdir}/libafshcrypto.a
%{_libdir}/libafshcrypto.so
%{_libdir}/libafsrfc3961.a
%{_libdir}/libuafs_pic.a
%{_mandir}/man1/rxgen.*
%{_mandir}/man1/afs_compile_et.*

%files krb5
%defattr(-,root,root)
%{_bindir}/aklog
%{_bindir}/klog.krb5
%{_bindir}/asetkey
%{_mandir}/man1/aklog.*
%{_mandir}/man1/klog.krb5.1.gz
%{_mandir}/man8/asetkey.*

%files server-firewalld
%defattr(-,root,root)
%{_prefix}/lib/firewalld/services/afs3-bos.xml
%{_prefix}/lib/firewalld/services/afs3-fileserver.xml
%{_prefix}/lib/firewalld/services/afs3-prserver.xml
%{_prefix}/lib/firewalld/services/afs3-update.xml
%{_prefix}/lib/firewalld/services/afs3-vlserver.xml
%{_prefix}/lib/firewalld/services/afs3-volser.xml

##############################################################################
###
### openafs.spec change log
###
##############################################################################
%changelog
* Fri Aug 30 2019 Alexander Boström <abo@kth.se> - 1.8.3-1.0.kth.7
- do not build kernel module

* Fri Aug 30 2019 Alexander Boström <abo@kth.se> - 1.8.3-1.0.kth.6
- Cleanup using rpmlint

* Fri Aug 30 2019 Alexander Boström <abo@kth.se> - 1.8.3-1.0.kth.5
- Cleanup.

* Fri Aug 30 2019 Alexander Boström <abo@kth.se> - 1.8.3-1.0.kth.4
- Fix distro version ifs

* Fri Aug 30 2019 Alexander Boström <abo@kth.se> - 1.8.3-1.0.kth.3
- Remove transarc subpackages

* Fri Aug 30 2019 Alexander Boström <abo@kth.se> - 1.8.3-1.0.kth.2
- 1.8.3 without client

* Fri Aug 30 2019 Alexander Boström <abo@kth.se> - 1.8.3-1.0.kth.1
- 1.8.3 without kernel module

* Wed Mar 20 2019 Jonathan S. Billings <jsbillin@umich.edu> - 1.8.3-0.pre1
- Packaged version 1.8.3pre1
- Add 'make' as a dependency for dkms-openafs

* Mon Feb 11 2019 Jonathan S. Billings <jsbillin@umich.edu> - 1.8.2-3
- Add firewalld subpackages to define service ports

* Wed Jan 23 2019 Jonathan S. Billings <jsbillin@umich.edu> - 1.8.2-2
- Add patches to address changes in linux 4.20 kernels
- rebuild autoconf due to patches

* Thu Sep 13 2018 Jonathan S. Billings <jsbillin@umich.edu> - 1.8.2-1
- Building 1.8.2
- Add patches to fix bugs introduced in OPENAFS-SA-2018-001 and
  OPENAFS-SA-2018-003, one of which led to compile errors.

* Fri Apr 13 2018 Jonathan S. Billings <jsbillin@umich.edu> - 1.8.0-1
- Building 1.8.0 final release

* Fri Jan 5 2018 Jonathan S. Billings <jsbillin@umich.edu> - 1.8.0-0.pre4
- Building 1.8.0 pre4

* Tue Dec 5 2017 Jonathan S. Billings <jsbillin@umich.edu> - 1.8.0-0.pre3
- Building 1.8.0 pre3

- Disable packaging of kaserver, pam_afs pam modules, kpasswd, man pages
* Wed Dec 14 2016 Jonathan S. Billings <jsbillin@umich.edu> - 1.8.0-0.pre1
- Building 1.8.0 pre1 alpha
- Disable packaging of kaserver, pam_afs pam modules, kpasswd, man pages
  and related software
- Include dkms package (from openafs-kmod spec file)
  
* Thu Dec 01 2016 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.20-1
- Bumped to 1.6.20

* Mon Nov 14 2016 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.19-1
- Bumped to 1.6.19

* Wed Jul 20 2016 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.18.2-1
- Bumped to 1.6.18.2

* Mon May 9 2016 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.18-1
- Bumped to 1.6.18

* Wed Mar 16 2016 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.17-1
- Bumped to 1.6.17
- Changed systemd units from 0755 to 0644 permissions

* Thu Dec 17 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.16-1
- Bumped to 1.6.16

* Wed Oct 28 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.15-1
- Bumped to 1.6.15
- Addresses CVE-2015-7762 and CVE-2015-7763

* Thu Sep 24 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.14.1-2
- Ignore LD hardening added in Fedora 23

* Tue Sep 22 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.14.1-1
- Bumped to 1.6.14.1

* Mon Aug 17 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.14-1
- Bumped to 1.6.14

* Mon Jul 20 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.12-1.1
- Replace source tarballs with ones prepared by openafs.org

* Mon Jul 06 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.12-1
- rebuilt against 1.6.12

* Fri Jun 05 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.11.1-3
- Create an rpmtrans scriptlet to deal with a removing a directory where
  a symlink will eventually be created.

* Mon May 18 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.11.1-2
- Include our own openafs-client.service, which fixes several startup
  issues.

* Mon May 18 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.11.1-1
- rebuilt against 1.6.11.1

* Mon Mar 02 2015 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.11-1
- rebuilt against 1.6.11

* Wed Oct  1 2014 Jonathan S. Billings <jsbillin@umich.edu> - 1.6.9-1
- Created initial spec file

