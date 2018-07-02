Name:           b2b_to_flume
Version:        2.1
Release:        1%{?dist}
Summary:        Cron job to run delim_to_json.py

Group:          B2B
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       delim_to_json, cronie

%description
The b2b_to_flume.sh script runs the delim_to_json.py program to convert an
input file into JSON, and then push that json file to a flume directory.


%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d $RPM_BUILD_ROOT/%{_bindir}
install -m 755 agent/B2B/%{name}.sh $RPM_BUILD_ROOT/%{_bindir}/%{name}.sh

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{_bindir}/%{name}.sh


%changelog
* Mon Dec  8 2014 Alan Brenner <alan.brenner@teradata.com> 2.1
- Correct path for delim_to_json.py
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Rework needed for the new directory structure
* Tue Oct 15 2014 Alan Brenner <alan.brenner@teradata.com> 1.0
- Initial RPM release
