# spec file for php-pecl-jsonc
#
# Copyright (c) 2013 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/3.0/
#
# Please, preserve the changelog entries
#
%{!?__pecl:      %{expand: %%global __pecl      %{_bindir}/pecl}}

%global pecl_name  json
%global proj_name  jsonc

%if "%{php_version}" > "5.5"
%global ext_name     json
%else
%global ext_name     jsonc
%endif

%if 0%{?fedora} < 19
%global with_libjson 0
%else
%global with_libjson 1
%endif


Summary:       Support for JSON serialization
Name:          php-pecl-%{proj_name}
Version:       1.3.2
Release:       2%{?dist}
License:       PHP
Group:         Development/Languages
URL:           http://pecl.php.net/package/%{proj_name}
Source0:       http://pecl.php.net/get/%{proj_name}-%{version}.tgz

BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: php-devel >= 5.4
BuildRequires: php-pear
BuildRequires: pcre-devel
%if %{with_libjson}
BuildRequires: json-c-devel >= 0.11
%endif

# partial fix to decode string with null-byte (only in value)
# https://github.com/remicollet/pecl-json-c/issues/7
Patch0:        jsonc-nullbyte.patch

Requires(post): %{__pecl}
Requires(postun): %{__pecl}
Requires:      php(zend-abi) = %{php_zend_api}
Requires:      php(api) = %{php_core_api}

Provides:      php-%{pecl_name} = %{version}
Provides:      php-%{pecl_name}%{?_isa} = %{version}
Provides:      php-pecl(%{pecl_name}) = %{version}
Provides:      php-pecl(%{pecl_name})%{?_isa} = %{version}
Provides:      php-pecl(%{proj_name}) = %{version}
Provides:      php-pecl(%{proj_name})%{?_isa} = %{version}
Obsoletes:     php-pecl-json < 1.3.1-2
Provides:      php-pecl-json = %{version}-%{release}
Provides:      php-pecl-json%{?_isa} = %{version}-%{release}

# Other third party repo stuff
Obsoletes:     php54-pecl-%{proj_name}
%if "%{php_version}" > "5.5"
Obsoletes:     php55-pecl-%{proj_name}
%endif

# Filter private shared
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}


%description
The %{name} module will add support for JSON (JavaScript Object Notation)
serialization to PHP.

This is a dropin alternative to standard PHP JSON extension which
use the json-c library parser.


%package devel
Summary:       JSON developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      php-devel%{?_isa}

%description devel
These are the files needed to compile programs using JSON serializer.

%if 0%{?rhel} == 5 && "%{php_version}" > "5.5"
%package -n php-json
Summary:       Meta package fo json extension
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}

%description  -n php-json
Meta package fo json extension.
Only used to be the best provider for php-json.
%endif


%prep
%setup -q -c 
cd %{proj_name}-%{version}

%patch0 -p1

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_JSON_VERSION/{s/.* "//;s/".*$//;p}' php_json.h )
if test "x${extver}" != "x%{version}%{?prever:-%{prever}}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}%{?prever:-%{prever}}.
   exit 1
fi
cd ..

cat << 'EOF' | tee %{ext_name}.ini
; Enable %{ext_name} extension module
%if "%{ext_name}" == "json"
extension = %{pecl_name}.so
%else
; You must disable standard %{pecl_name}.so before you enable %{proj_name}.so
;extension = %{proj_name}.so
%endif
EOF

# duplicate for ZTS build
cp -pr %{proj_name}-%{version} %{proj_name}-zts


%build
cd %{proj_name}-%{version}
%{_bindir}/phpize
%configure \
%if %{with_libjson}
  --with-libjson \
%endif
%if "%{ext_name}" == "jsonc"
  --with-jsonc \
%endif
  --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}

cd ../%{proj_name}-zts
%{_bindir}/zts-phpize
%configure \
%if %{with_libjson}
  --with-libjson \
%endif
%if "%{ext_name}" == "jsonc"
  --with-jsonc \
%endif
  --with-php-config=%{_bindir}/zts-php-config
make %{?_smp_mflags}


%install
rm -rf %{buildroot}
# Install the NTS stuff
make -C %{proj_name}-%{version} \
     install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ext_name}.ini %{buildroot}%{php_inidir}/%{ext_name}.ini

# Install the ZTS stuff
make -C %{proj_name}-zts \
     install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{ext_name}.ini %{buildroot}%{php_ztsinidir}/%{ext_name}.ini

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

%check
cd %{proj_name}-%{version}

TEST_PHP_EXECUTABLE=%{_bindir}/php \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{ext_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{_bindir}/php -n run-tests.php

cd ../%{proj_name}-zts

TEST_PHP_EXECUTABLE=%{__ztsphp} \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{ext_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{__ztsphp} -n run-tests.php


%post
%{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :


%postun
if [ $1 -eq 0 ] ; then
    %{pecl_uninstall} %{proj_name} >/dev/null || :
fi


%clean
rm -rf %{buildroot}


%files
%defattr(-,root,root,-)
%doc %{proj_name}-%{version}%{?prever}/{LICENSE,CREDITS,README.md}
%config(noreplace) %{php_inidir}/%{ext_name}.ini
%config(noreplace) %{php_ztsinidir}/%{ext_name}.ini
%{php_extdir}/%{ext_name}.so
%{php_ztsextdir}/%{ext_name}.so
%{pecl_xmldir}/%{name}.xml


%files devel
%defattr(-,root,root,-)
%{php_incldir}/ext/json
%{php_ztsincldir}/ext/json

%if 0%{?rhel} == 5 && "%{php_version}" > "5.5"
%files -n php-json
%defattr(-,root,root,-)
%endif

#
# Note to remi : remember to always build in remi-test first
#
%changelog
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
