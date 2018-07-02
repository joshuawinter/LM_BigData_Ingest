Name:           Google
Version:        2.3
Release:        1%{?dist}
Summary:        Google API client

Group:          API
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       python >= 2.6

%description
Run by the api_client.sh script, this extracts reporting data from the Google
AdWords API into JSON.


%prep
%setup -q

%check
export PYTHONPATH=edge/API
python test/API/%{name}_test.py

%install
rm -rf $RPM_BUILD_ROOT
#install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/LM
#install -m 640 google.yaml $RPM_BUILD_ROOT%{_sysconfdir}/LM/google.yaml
install -m 755 -d $RPM_BUILD_ROOT%{_bindir}
install -m 755 edge/API/%{name}.py $RPM_BUILD_ROOT%{_bindir}/%{name}.py

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
#%config %{_sysconfdir}/LM/google.yaml
%{_bindir}/%{name}.py


%changelog
* Mon Dec  8 2014 Alan Brenner <alan.brenner@teradata.com> 2.3
- Google has dropped MaxCpc, discovered by John Morgan. Python googleads 2.3.0+ now required.
* Mon Dec  8 2014 Alan Brenner <alan.brenner@teradata.com> 2.2
- Correct PyDoc on output parameter type.
* Sun Dec  7 2014 Alan Brenner <alan.brenner@teradata.com> 2.1
- Remove dependency on api_client, since it depends on this.
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Rework needed for the new directory structure
* Wed Oct 29 2014 Alan Brenner <alan.brenner@teradata.com> 1.2
- Handle connection issues, improve performance, add data types
* Thu Oct 16 2014 Alan Brenner <alan.brenner@teradata.com> 1.0
- Initial RPM release
