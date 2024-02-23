%global debug_package %{nil}
%global plugin_name jpegphoto

%global ipa_python3_sitelib %{python3_sitelib}

Name:           freeipa-%{plugin_name}
Version:        0.1.7
Release:        2%{?dist}
Summary:        user avatar integration for FreeIPA

BuildArch:      noarch

License:        GPLv3+
URL:            https://github.com/jasperroloff/freeipa-jpegphoto
Source0:        freeipa-jpegphoto-%{version}.tar.gz


BuildRequires: ipa-server-common >= 4.6.0
BuildRequires: python3-devel
BuildRequires: python3-ipaserver >= 4.6.0

Requires(post): python3-ipa-%{plugin_name}-server
Requires: python3-ipa-%{plugin_name}-server

%description
A FreeIPA extension to add avatar field to user objects.

%package -n python3-ipa-%{plugin_name}-server
Summary: Server side of user avatar with FreeIPA
License: GPLv3+
Requires: python3-ipaserver

%description -n python3-ipa-%{plugin_name}-server
A FreeIPA extension to add avatar field to user objects.
This package adds server-side support for FreeIPA.

%prep
%autosetup

%build
touch debugfiles.list

%install
rm -rf $RPM_BUILD_ROOT
%__mkdir_p %buildroot/%_datadir/ipa/schema.d
%__mkdir_p %buildroot/%_datadir/ipa/updates
%__mkdir_p %buildroot/%_datadir/ipa/ui/js/plugins/%{plugin_name}

targets="ipaserver"
for s in $targets ; do
    %__mkdir_p %buildroot/%{ipa_python3_sitelib}/$s/plugins
    for j in $(find plugin/$s/plugins -name '*.py') ; do
        %__cp $j %buildroot/%{ipa_python3_sitelib}/$s/plugins
    done
done

#for j in $(find plugin/schema.d -name '*.ldif') ; do
#    %__cp $j %buildroot/%_datadir/ipa/schema.d
#done

#for j in $(find plugin/updates -name '*.update') ; do
#    %__cp $j %buildroot/%_datadir/ipa/updates
#done

for j in $(find plugin/ui -name '*.js') ; do
    %__cp $j %buildroot/%_datadir/ipa/ui/js/plugins/%{plugin_name}
done

%posttrans
ipa_interp=python3
$ipa_interp -c "import sys; from ipaserver.install import installutils; sys.exit(0 if installutils.is_ipa_configured() else 1);" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    # This must be run in posttrans so that updates from previous
    # execution that may no longer be shipped are not applied.
    /usr/sbin/ipa-server-upgrade --quiet >/dev/null || :

    # Restart IPA processes. This must be also run in postrans so that plugins
    # and software is in consistent state
    # NOTE: systemd specific section

    /bin/systemctl is-enabled ipa.service >/dev/null 2>&1
    if [  $? -eq 0 ]; then
        /bin/systemctl restart ipa.service >/dev/null 2>&1 || :
    fi
fi

%files
%license LICENSE
#%_datadir/ipa/schema.d/*
#%_datadir/ipa/updates/*
%_datadir/ipa/ui/js/plugins/%{plugin_name}/*

%files -n python3-ipa-%{plugin_name}-server
%{ipa_python3_sitelib}/ipaserver/plugins/*

%changelog
* Fri Feb 23 2024 Jasper Roloff <jasperroloff@gmail.com> 0.1.7-2
- GitHub actions: fix syntax (jasperroloff@gmail.com)

* Fri Feb 23 2024 Jasper Roloff <jasperroloff@gmail.com> 0.1.7-1
- GitHub actions: build for multiple targets (jasperroloff@gmail.com)

* Fri Feb 23 2024 Jasper Roloff <jasperroloff@gmail.com> 0.1.6-1
- upgrade fedora to 37 (jasperroloff@gmail.com)

* Fri Feb 23 2024 Jasper Roloff <jasperroloff@gmail.com> 0.1.5-1
- upgrade fedora to 36 (jasperroloff@gmail.com)

* Sun Jun 19 2022 Jasper Roloff <jasperroloff@gmail.com> 0.1.4-1
- upgrade github actions (jasperroloff@gmail.com)
- fix build (jasperroloff@gmail.com)
- upgrade to fedora 35 (jasperroloff@gmail.com)

* Tue Aug 10 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.3-1
- add hint for original project (jasperroloff@gmail.com)

* Tue Aug 10 2021 Jasper Roloff <jasperroloff@gmail.com>
- add hint for original project (jasperroloff@gmail.com)

* Tue Aug 10 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.2-1
- update gitignore (jasperroloff@gmail.com)

* Tue Aug 10 2021 Jasper Roloff <jasperroloff@gmail.com>
- update gitignore (jasperroloff@gmail.com)

* Tue Aug 10 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.1-1
- 

* Tue Aug 10 2021 Jasper Roloff <jasperroloff@gmail.com> 0.1.0-1
- Initial release
