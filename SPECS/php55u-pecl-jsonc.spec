# IUS spec file for php55u-pecl-jsonc, forked from:
#
# spec file for php-pecl-jsonc
#
# Copyright (c) 2013 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#

%global pecl_name  json
%global proj_name  jsonc
%global ini_name   40-%{pecl_name}.ini
%global with_zts 0%{?__ztsphp:1}

%define php_base php55u


Summary:       Support for JSON serialization
Name:          %{php_base}-pecl-%{proj_name}
Version:       1.3.10
Release:       1.ius%{?dist}
# PHP extension is PHP
# jsonc-c is MIT
# json-c/linkhask.c is Public Domain
License:       PHP and MIT and Public Domain
Group:         Development/Languages
URL:           http://pecl.php.net/package/%{proj_name}
Source0:       http://pecl.php.net/get/%{proj_name}-%{version}.tgz

BuildRequires: %{php_base}-devel
BuildRequires: %{php_base}-pear
BuildRequires: pcre-devel

Requires(post): %{php_base}-pear
Requires(postun): %{php_base}-pear
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api) = %{php_core_api}

# provide the stock names
Provides:      php-pecl-%{proj_name} = %{version}
Provides:      php-pecl-%{proj_name}%{?_isa} = %{version}
Provides:      php-pecl-%{pecl_name} = %{version}
Provides:      php-pecl-%{pecl_name}%{?_isa} = %{version}
Provides:      %{php_base}-pecl-%{pecl_name} = %{version}
Provides:      %{php_base}-pecl-%{pecl_name}%{?_isa} = %{version}

# provide the stock and IUS names without pecl
Provides:      php-%{pecl_name} = %{version}
Provides:      php-%{pecl_name}%{?_isa} = %{version}
Provides:      php-%{proj_name} = %{version}
Provides:      php-%{proj_name}%{?_isa} = %{version}
Provides:      %{php_base}-%{pecl_name} = %{version}
Provides:      %{php_base}-%{pecl_name}%{?_isa} = %{version}
Provides:      %{php_base}-%{proj_name} = %{version}
Provides:      %{php_base}-%{proj_name}%{?_isa} = %{version}

# provide the stock and IUS names in pecl() format
Provides:      php-pecl(%{pecl_name}) = %{version}
Provides:      php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:      php-pecl(%{proj_name}) = %{version}
Provides:      php-pecl(%{proj_name})%{?_isa} = %{version}
Provides:      %{php_base}-pecl(%{pecl_name}) = %{version}
Provides:      %{php_base}-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:      %{php_base}-pecl(%{proj_name}) = %{version}
Provides:      %{php_base}-pecl(%{proj_name})%{?_isa} = %{version}

# conflict with the stock name
Conflicts:     php-pecl-%{proj_name} < %{version}

# RPM 4.8
%{?filter_provides_in: %filter_provides_in %{php_extdir}/.*\.so$}
%{?filter_setup}
# RPM 4.9
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_extdir}/.*\\.so$


%description
The %{name} module will add support for JSON (JavaScript Object Notation)
serialization to PHP.

This is a dropin alternative to standard PHP JSON extension which
use the json-c library parser.


%package devel
Summary:       JSON developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      %{php_base}-devel%{?_isa}

Provides:      php-pecl-%{proj_name}-devel = %{version}
Provides:      php-pecl-%{proj_name}-devel%{?_isa} = %{version}
Conflicts:     php-pecl-%{proj_name}-devel < %{version}


%description devel
These are the files needed to compile programs using JSON serializer.


%prep
%setup -q -c
mv %{proj_name}-%{version} NTS

pushd NTS

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_JSON_VERSION/{s/.* "//;s/".*$//;p}' php_json.h )
if test "x${extver}" != "x%{version}%{?prever:%{prever}}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever:%{prever}}.
   exit 1
fi
popd

cat << 'EOF' | tee %{ini_name}
; Enable %{pecl_name} extension module
extension = %{pecl_name}.so
EOF

%if %{with_zts}
# duplicate for ZTS build
cp -pr NTS ZTS
%endif


%build
pushd NTS
%{_bindir}/phpize
%configure \
  --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}
popd

%if %{with_zts}
pushd ZTS
%{_bindir}/zts-phpize
%configure \
  --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}
popd
%endif


%install
# Install the NTS stuff
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_inidir}/%{ini_name}

%if %{with_zts}
# Install the ZTS stuff
make -C ZTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ini_name} %{buildroot}%{php_ztsinidir}/%{ini_name}
%endif

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{proj_name}.xml

# Test & Documentation
for i in $(grep 'role="test"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in $(grep 'role="doc"' package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 NTS/$i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
pushd NTS
TEST_PHP_EXECUTABLE=%{__php} \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__php} -n run-tests.php
popd

%if %{with_zts}
pushd ZTS
TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php
popd
%endif


%post
%{pecl_install} %{pecl_xmldir}/%{proj_name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{proj_name} >/dev/null || :
fi


%files
%{?_licensedir:%license NTS/LICENSE}
%{?_licensedir:%license NTS/json-c/COPYING}
%doc %{pecl_docdir}/%{pecl_name}
%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so
%if %{with_zts}
%config(noreplace) %{php_ztsinidir}/%{ini_name}
%{php_ztsextdir}/%{pecl_name}.so
%endif
%{pecl_xmldir}/%{proj_name}.xml


%files devel
%{php_incldir}/ext/json
%if %{with_zts}
%{php_ztsincldir}/ext/json
%endif
%doc %{pecl_testdir}/%{pecl_name}


%changelog
* Wed Jun 15 2016 Ben Harper <ben.harper@rackspace.com> - 1.3.10-1.ius
- Latest upstream

* Tue Mar 22 2016 Carl George <carl.george@rackspace.com> - 1.3.9-2.ius
- Clean up provides
- Clean up conflicts
- Clean up filters
- ZTS cleanup
- Install package.xml as jsonc.xml, not %%{name}.xml
- Import license handling from Fedora

* Tue Sep 15 2015 Carl George <carl.george@rackspace.com> - 1.3.9-1.ius
- Latest upstream

* Tue Sep 08 2015 Ben Harper <ben.harper@rackspace.com> - 1.3.8-1.ius
- Latest upstream

* Wed Feb 18 2015 Carl George <carl.george@rackspace.com> - 1.3.7-1.ius
- Latest upstream

* Fri Oct 10 2014 Carl George <carl.george@rackspace.com> - 1.3.6-2.ius
- Conflict with stock package
- Use same provides as stock package
- Directly require the correct pear package, not /usr/bin/pecl

* Thu Oct 02 2014 Carl George <carl.george@rackspace.com> - 1.3.6-2.ius
- add numerical prefix to extension configuration file
- move documentation in pecl_docdir
- move tests in pecl_testdir (devel)

* Fri Aug 01 2014 Carl George <carl.george@rackspace.com> - 1.3.6-1.ius
- Latest sources from upstream

* Fri Apr 11 2014 Ben Harper <ben.harper@rackspace.com> - 1.3.5-1.ius
- Latest sources from upstream

* Tue Feb 25 2014 Ben Harper <ben.harper@rackspace.com> - 1.3.4-1.ius
- Latest sources from upstream

* Fri Dec 13 2013 Ben Harper <ben.harper@rackspace.com> - 1.3.3-1.ius
- Latest sources from upstream
- diable patch0, patched upstream

* Tue Nov 19 2013 Ben Harper <ben.harper@rackspace.com> - 1.3.2-4.ius
- removing --with-jsonc, see LP bug 1252833

* Thu Oct 24 2013 Ben Harper <ben.harper@rackspace.com> - 1.3.2-3.ius
- porting from php-pecl-jsonc-1.3.2-2.fc19.src.rpm

* Thu Sep 26 2013 Remi Collet <rcollet@redhat.com> - 1.3.2-2
- fix decode of string value with null-byte

* Mon Sep  9 2013 Remi Collet <rcollet@redhat.com> - 1.3.2-1
- release 1.3.2 (stable)

* Mon Jun 24 2013 Remi Collet <rcollet@redhat.com> - 1.3.1-2.el5.2
- add metapackage "php-json" to fix upgrade issue (EL-5)

* Wed Jun 12 2013 Remi Collet <rcollet@redhat.com> - 1.3.1-2
- rename to php-pecl-jsonc

* Wed Jun 12 2013 Remi Collet <rcollet@redhat.com> - 1.3.1-1
- release 1.3.1 (beta)

* Tue Jun  4 2013 Remi Collet <rcollet@redhat.com> - 1.3.0-1
- release 1.3.0 (beta)
- use system json-c when available (fedora >= 20)
- use jsonc name for module and configuration

* Mon Apr 29 2013 Remi Collet <rcollet@redhat.com> - 1.3.0-0.3
- rebuild with latest changes
- use system json-c library
- temporarily rename to jsonc-c.so

* Sat Apr 27 2013 Remi Collet <rcollet@redhat.com> - 1.3.0-0.2
- rebuild with latest changes

* Sat Apr 27 2013 Remi Collet <rcollet@redhat.com> - 1.3.0-0.1
- initial package
