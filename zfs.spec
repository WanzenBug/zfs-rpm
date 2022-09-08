%global _sbindir    /sbin
%global _libdir     /%{_lib}

# Set the default udev directory based on distribution.
%if %{undefined _udevdir}
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7 || 0%{?centos} >= 7
%global _udevdir    %{_prefix}/lib/udev
%else
%global _udevdir    /lib/udev
%endif
%endif

# Set the default udevrule directory based on distribution.
%if %{undefined _udevruledir}
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7 || 0%{?centos} >= 7
%global _udevruledir    %{_prefix}/lib/udev/rules.d
%else
%global _udevruledir    /lib/udev/rules.d
%endif
%endif

# Set the default dracut directory based on distribution.
%if %{undefined _dracutdir}
%if 0%{?fedora} >= 17 || 0%{?rhel} >= 7 || 0%{?centos} >= 7
%global _dracutdir  %{_prefix}/lib/dracut
%else
%global _dracutdir  %{_prefix}/share/dracut
%endif
%endif

%if %{undefined _initconfdir}
%global _initconfdir /etc/sysconfig
%endif

%if %{undefined _unitdir}
%global _unitdir %{_prefix}/lib/systemd/system
%endif

%if %{undefined _presetdir}
%global _presetdir %{_prefix}/lib/systemd/system-preset
%endif

%if %{undefined _modulesloaddir}
%global _modulesloaddir %{_prefix}/lib/modules-load.d
%endif

%if %{undefined _systemdgeneratordir}
%global _systemdgeneratordir %{_prefix}/lib/systemd/system-generators
%endif

%if %{undefined _pkgconfigdir}
%global _pkgconfigdir %{_prefix}/%{_lib}/pkgconfig
%endif

%bcond_with    debug
%bcond_with    debuginfo
%bcond_with    asan
%bcond_with    systemd
%bcond_with    pam

# Generic enable switch for systemd
%if %{with systemd}
%define _systemd 1
%endif

# RHEL >= 7 comes with systemd
%if 0%{?rhel} >= 7
%define _systemd 1
%endif

# Fedora >= 15 comes with systemd, but only >= 18 has
# the proper macros
%if 0%{?fedora} >= 18
%define _systemd 1
%endif

# opensuse >= 12.1 comes with systemd, but only >= 13.1
# has the proper macros
%if 0%{?suse_version} >= 1310
%define _systemd 1
%endif

# When not specified default to distribution provided version.  This
# is normally Python 3, but for RHEL <= 7 only Python 2 is provided.
%if %{undefined __use_python}
%if 0%{?rhel} && 0%{?rhel} <= 7
%define __python                  /usr/bin/python2
%define __python_pkg_version      2
%define __python_cffi_pkg         python-cffi
%define __python_setuptools_pkg   python-setuptools
%else
%define __python                  /usr/bin/python3
%define __python_pkg_version      3
%define __python_cffi_pkg         python3-cffi
%define __python_setuptools_pkg   python3-setuptools
%endif
%else
%define __python                  %{__use_python}
%define __python_pkg_version      %{__use_python_pkg_version}
%define __python_cffi_pkg         python%{__python_pkg_version}-cffi
%define __python_setuptools_pkg   python%{__python_pkg_version}-setuptools
%endif
%define __python_sitelib          %(%{__python} -Esc "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

# By default python-pyzfs is enabled, with the exception of
# RHEL 6 which by default uses Python 2.6 which is too old.
%if 0%{?rhel} == 6
%bcond_with    pyzfs
%else
%bcond_without pyzfs
%endif

Name:           zfs
Version:        2.1.5
Release:        1%{?dist}
Summary:        Commands to control the kernel modules and libraries

Group:          System Environment/Kernel
License:        CDDL
URL:            https://github.com/openzfs/zfs
Source0:        https://github.com/openzfs/zfs/releases/download/%{name}-%{version}/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:       libzpool5 = %{version}
Requires:       libnvpair3 = %{version}
Requires:       libuutil3 = %{version}
Requires:       libzfs5 = %{version}
Obsoletes:      spl

# zfs-fuse provides the same commands and man pages that OpenZFS does.
# Renaming those on either side would conflict with all available documentation.
Conflicts:      zfs-fuse

%if 0%{?rhel}%{?fedora}%{?suse_version}
BuildRequires:  gcc, make
BuildRequires:  zlib-devel
BuildRequires:  libuuid-devel
BuildRequires:  libblkid-devel
BuildRequires:  libudev-devel
BuildRequires:  libattr-devel
BuildRequires:  openssl-devel
%if 0%{?fedora} || 0%{?rhel} >= 8 || 0%{?centos} >= 8
BuildRequires:  libtirpc-devel
%endif

%if (0%{?fedora}%{?suse_version}) || (0%{?rhel} && 0%{?rhel} < 9)
# We don't directly use it, but if this isn't installed, rpmbuild as root can
# crash+corrupt rpmdb
# See issue #12071
BuildRequires:  ncompress
%endif

%if %{with pam}
BuildRequires:  pam-devel
%endif

Requires:       openssl
%if 0%{?_systemd}
BuildRequires: systemd
%endif

%endif

%if 0%{?_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

# The zpool iostat/status -c scripts call some utilities like lsblk and iostat
Requires:  util-linux
Requires:  sysstat

%description
This package contains the core ZFS command line utilities.

%package -n libzpool5
Summary:        Native ZFS pool library for Linux
Group:          System Environment/Kernel
Obsoletes:      libzpool2
Obsoletes:      libzpool4

%description -n libzpool5
This package contains the zpool library, which provides support
for managing zpools

%if %{defined ldconfig_scriptlets}
%ldconfig_scriptlets -n libzpool5
%else
%post -n libzpool5 -p /sbin/ldconfig
%postun -n libzpool5 -p /sbin/ldconfig
%endif

%package -n libnvpair3
Summary:        Solaris name-value library for Linux
Group:          System Environment/Kernel
Obsoletes:      libnvpair1

%description -n libnvpair3
This package contains routines for packing and unpacking name-value
pairs.  This functionality is used to portably transport data across
process boundaries, between kernel and user space, and can be used
to write self describing data structures on disk.

%if %{defined ldconfig_scriptlets}
%ldconfig_scriptlets -n libnvpair3
%else
%post -n libnvpair3 -p /sbin/ldconfig
%postun -n libnvpair3 -p /sbin/ldconfig
%endif

%package -n libuutil3
Summary:        Solaris userland utility library for Linux
Group:          System Environment/Kernel
Obsoletes:      libuutil1

%description -n libuutil3
This library provides a variety of compatibility functions for OpenZFS:
 * libspl: The Solaris Porting Layer userland library, which provides APIs
   that make it possible to run Solaris user code in a Linux environment
   with relatively minimal modification.
 * libavl: The Adelson-Velskii Landis balanced binary tree manipulation
   library.
 * libefi: The Extensible Firmware Interface library for GUID disk
   partitioning.
 * libshare: NFS, SMB, and iSCSI service integration for ZFS.

%if %{defined ldconfig_scriptlets}
%ldconfig_scriptlets -n libuutil3
%else
%post -n libuutil3 -p /sbin/ldconfig
%postun -n libuutil3 -p /sbin/ldconfig
%endif

# The library version is encoded in the package name.  When updating the
# version information it is important to add an obsoletes line below for
# the previous version of the package.
%package -n libzfs5
Summary:        Native ZFS filesystem library for Linux
Group:          System Environment/Kernel
Obsoletes:      libzfs2
Obsoletes:      libzfs4

%description -n libzfs5
This package provides support for managing ZFS filesystems

%if %{defined ldconfig_scriptlets}
%ldconfig_scriptlets -n libzfs5
%else
%post -n libzfs5 -p /sbin/ldconfig
%postun -n libzfs5 -p /sbin/ldconfig
%endif

%package -n libzfs5-devel
Summary:        Development headers
Group:          System Environment/Kernel
Requires:       libzfs5 = %{version}
Requires:       libzpool5 = %{version}
Requires:       libnvpair3 = %{version}
Requires:       libuutil3 = %{version}
Provides:       libzpool5-devel
Provides:       libnvpair3-devel
Provides:       libuutil3-devel
Obsoletes:      zfs-devel
Obsoletes:      libzfs2-devel
Obsoletes:      libzfs4-devel

%description -n libzfs5-devel
This package contains the header files needed for building additional
applications against the ZFS libraries.

%package test
Summary:        Test infrastructure
Group:          System Environment/Kernel
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       parted
Requires:       lsscsi
Requires:       mdadm
Requires:       bc
Requires:       ksh
Requires:       fio
Requires:       acl
Requires:       sudo
Requires:       sysstat
Requires:       libaio
Requires:       python%{__python_pkg_version}
%if 0%{?rhel}%{?fedora}%{?suse_version}
BuildRequires:  libaio-devel
%endif
AutoReqProv:    no

%description test
This package contains test infrastructure and support scripts for
validating the file system.

%package dracut
Summary:        Dracut module
Group:          System Environment/Kernel
BuildArch:	noarch
Requires:       %{name} >= %{version}
Requires:       dracut
Requires:       /usr/bin/awk
Requires:       grep

%description dracut
This package contains a dracut module used to construct an initramfs
image which is ZFS aware.

%if %{with pyzfs}
%package -n python%{__python_pkg_version}-pyzfs
Summary:        Python %{python_version} wrapper for libzfs_core
Group:          Development/Languages/Python
License:        Apache-2.0
BuildArch:      noarch
Requires:       libzfs5 = %{version}
Requires:       libnvpair3 = %{version}
Requires:       libffi
Requires:       python%{__python_pkg_version}
Requires:       %{__python_cffi_pkg}
%if 0%{?rhel}%{?fedora}%{?suse_version}
%if 0%{?rhel} >= 8 || 0%{?centos} >= 8 || 0%{?fedora} >= 28
BuildRequires:  python3-packaging
%else
BuildRequires:  python-packaging
%endif
BuildRequires:  python%{__python_pkg_version}-devel
BuildRequires:  %{__python_cffi_pkg}
BuildRequires:  %{__python_setuptools_pkg}
BuildRequires:  libffi-devel
%endif

%description -n python%{__python_pkg_version}-pyzfs
This package provides a python wrapper for the libzfs_core C library.
%endif

%if 0%{?_initramfs}
%package initramfs
Summary:        Initramfs module
Group:          System Environment/Kernel
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       %{name} = %{version}-%{release}
Requires:       initramfs-tools

%description initramfs
This package contains a initramfs module used to construct an initramfs
image which is ZFS aware.
%endif

%prep
%if %{with debug}
    %define debug --enable-debug
%else
    %define debug --disable-debug
%endif

%if %{with debuginfo}
    %define debuginfo --enable-debuginfo
%else
    %define debuginfo --disable-debuginfo
%endif

%if %{with asan}
    %define asan --enable-asan
%else
    %define asan --disable-asan
%endif

%if 0%{?_systemd}
    %define systemd --enable-systemd --with-systemdunitdir=%{_unitdir} --with-systemdpresetdir=%{_presetdir} --with-systemdmodulesloaddir=%{_modulesloaddir} --with-systemdgeneratordir=%{_systemdgeneratordir} --disable-sysvinit
    %define systemd_svcs zfs-import-cache.service zfs-import-scan.service zfs-mount.service zfs-share.service zfs-zed.service zfs.target zfs-import.target zfs-volume-wait.service zfs-volumes.target
%else
    %define systemd --enable-sysvinit --disable-systemd
%endif

%if %{with pyzfs}
    %define pyzfs --enable-pyzfs
%else
    %define pyzfs --disable-pyzfs
%endif

%if %{with pam}
    %define pam --enable-pam
%else
    %define pam --disable-pam
%endif

%setup -q

%build
%configure \
    --with-config=user \
    --with-udevdir=%{_udevdir} \
    --with-udevruledir=%{_udevruledir} \
    --with-dracutdir=%{_dracutdir} \
    --with-pamconfigsdir=%{_datadir}/pam-configs \
    --with-pammoduledir=%{_libdir}/security \
    --with-python=%{__python} \
    --with-pkgconfigdir=%{_pkgconfigdir} \
    --disable-static \
    %{debug} \
    %{debuginfo} \
    %{asan} \
    %{systemd} \
    %{pam} \
    %{pyzfs}
make %{?_smp_mflags}

%install
%{__rm} -rf $RPM_BUILD_ROOT
make install DESTDIR=%{?buildroot}
find %{?buildroot}%{_libdir} -name '*.la' -exec rm -f {} \;
%if 0%{!?__brp_mangle_shebangs:1}
find %{?buildroot}%{_bindir} \
    \( -name arc_summary -or -name arcstat -or -name dbufstat \) \
    -exec %{__sed} -i 's|^#!.*|#!%{__python}|' {} \;
find %{?buildroot}%{_datadir} \
    \( -name test-runner.py -or -name zts-report.py \) \
    -exec %{__sed} -i 's|^#!.*|#!%{__python}|' {} \;
%endif

%post
%if 0%{?_systemd}
%if 0%{?systemd_post:1}
%systemd_post %{systemd_svcs}
%else
if [ "$1" = "1" -o "$1" = "install" ] ; then
    # Initial installation
    systemctl preset %{systemd_svcs} >/dev/null || true
fi
%endif
%else
if [ -x /sbin/chkconfig ]; then
    /sbin/chkconfig --add zfs-import
    /sbin/chkconfig --add zfs-load-key
    /sbin/chkconfig --add zfs-mount
    /sbin/chkconfig --add zfs-share
    /sbin/chkconfig --add zfs-zed
fi
%endif
exit 0

# On RHEL/CentOS 7 the static nodes aren't refreshed by default after
# installing a package.  This is the default behavior for Fedora.
%posttrans
%if 0%{?rhel} == 7 || 0%{?centos} == 7
systemctl restart kmod-static-nodes
systemctl restart systemd-tmpfiles-setup-dev
udevadm trigger
%endif

%preun
%if 0%{?_systemd}
%if 0%{?systemd_preun:1}
%systemd_preun %{systemd_svcs}
%else
if [ "$1" = "0" -o "$1" = "remove" ] ; then
    # Package removal, not upgrade
    systemctl --no-reload disable %{systemd_svcs} >/dev/null || true
    systemctl stop %{systemd_svcs} >/dev/null || true
fi
%endif
%else
if [ "$1" = "0" -o "$1" = "remove" ] && [ -x /sbin/chkconfig ]; then
    /sbin/chkconfig --del zfs-import
    /sbin/chkconfig --del zfs-load-key
    /sbin/chkconfig --del zfs-mount
    /sbin/chkconfig --del zfs-share
    /sbin/chkconfig --del zfs-zed
fi
%endif
exit 0

%postun
%if 0%{?_systemd}
%if 0%{?systemd_postun:1}
%systemd_postun %{systemd_svcs}
%else
systemctl --system daemon-reload >/dev/null || true
%endif
%endif

%files
# Core utilities
%{_sbindir}/*
%{_bindir}/raidz_test
%{_sbindir}/zgenhostid
%{_bindir}/zvol_wait
# Optional Python 2/3 scripts
%{_bindir}/arc_summary
%{_bindir}/arcstat
%{_bindir}/dbufstat
# Man pages
%{_mandir}/man1/*
%{_mandir}/man4/*
%{_mandir}/man5/*
%{_mandir}/man7/*
%{_mandir}/man8/*
# Configuration files and scripts
%{_libexecdir}/%{name}
%{_udevdir}/vdev_id
%{_udevdir}/zvol_id
%{_udevdir}/rules.d/*
%{_datadir}/%{name}/compatibility.d
%if ! 0%{?_systemd} || 0%{?_initramfs}
# Files needed for sysvinit and initramfs-tools
%{_sysconfdir}/%{name}/zfs-functions
%config(noreplace) %{_initconfdir}/zfs
%else
%exclude %{_sysconfdir}/%{name}/zfs-functions
%exclude %{_initconfdir}/zfs
%endif
%if 0%{?_systemd}
%{_unitdir}/*
%{_presetdir}/*
%{_modulesloaddir}/*
%{_systemdgeneratordir}/*
%else
%config(noreplace) %{_sysconfdir}/init.d/*
%endif
%config(noreplace) %{_sysconfdir}/%{name}/zed.d/*
%config(noreplace) %{_sysconfdir}/%{name}/zpool.d/*
%config(noreplace) %{_sysconfdir}/%{name}/vdev_id.conf.*.example
%attr(440, root, root) %config(noreplace) %{_sysconfdir}/sudoers.d/*
%if %{with pam}
%{_libdir}/security/*
%{_datadir}/pam-configs/*
%endif

%files -n libzpool5
%{_libdir}/libzpool.so.*

%files -n libnvpair3
%{_libdir}/libnvpair.so.*

%files -n libuutil3
%{_libdir}/libuutil.so.*

%files -n libzfs5
%{_libdir}/libzfs*.so.*

%files -n libzfs5-devel
%{_pkgconfigdir}/libzfs.pc
%{_pkgconfigdir}/libzfsbootenv.pc
%{_pkgconfigdir}/libzfs_core.pc
%{_libdir}/*.so
%{_includedir}/*
%doc AUTHORS COPYRIGHT LICENSE NOTICE README.md

%files test
%{_datadir}/%{name}/zfs-tests
%{_datadir}/%{name}/test-runner
%{_datadir}/%{name}/runfiles
%{_datadir}/%{name}/*.sh

%files dracut
%doc contrib/dracut/README.dracut.markdown
%{_dracutdir}/modules.d/*

%if %{with pyzfs}
%files -n python%{__python_pkg_version}-pyzfs
%doc contrib/pyzfs/README
%doc contrib/pyzfs/LICENSE
%defattr(-,root,root,-)
%{__python_sitelib}/libzfs_core/*
%{__python_sitelib}/pyzfs*
%endif

%if 0%{?_initramfs}
%files initramfs
%doc contrib/initramfs/README.initramfs.markdown
/usr/share/initramfs-tools/*
%else
# Since we're not building the initramfs package,
# ignore those files.
%exclude /usr/share/initramfs-tools
%endif
