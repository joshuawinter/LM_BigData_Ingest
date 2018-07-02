Name:           Bing
Version:        2.1
Release:        1%{?dist}
Summary:        Bing API client

Group:          API
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       python >= 2.6

%description
Run by the api_client.sh script, this extracts reporting data from the Bing API
into JSON.


%prep
%setup -q

%check
export PYTHONPATH=edge/API
python test/API/%{name}_test.py

%install
rm -rf $RPM_BUILD_ROOT
#install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/LM
#install -m 640 bing.ini $RPM_BUILD_ROOT%{_sysconfdir}/LM/bing.ini
install -m 755 -d $RPM_BUILD_ROOT%{_bindir}
install -m 755 edge/API/%{name}.py $RPM_BUILD_ROOT%{_bindir}/%{name}.py

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
#%config %{_sysconfdir}/LM/bing.ini
%{_bindir}/%{name}.py


%changelog
* Tue Dec  7 2014 Alan Brenner <alan.brenner@teradata.com> 2.1
- Remove dependency on api_client, since it depends on this.
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Rework needed for the new directory structure
* Tue Oct 21 2014 Alan Brenner <alan.brenner@teradata.com> 1.4
- Add option to use libcurl (needed for non-proxy access)
- Silence converstion message for AveragePosition.
* Fri Oct 17 2014 Alan Brenner <alan.brenner@teradata.com> 1.3
- Python 2.6 zipfile with bug fix
* Thu Oct 16 2014 Alan Brenner <alan.brenner@teradata.com> 1.0
- Initial RPM release
