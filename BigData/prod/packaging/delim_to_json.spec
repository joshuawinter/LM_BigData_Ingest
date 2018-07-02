Name:           delim_to_json
Version:        2.2
Release:        1%{?dist}
Summary:        Convert a delimited file into JSON

Group:          B2B
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       python >= 2.6

%description
Run by the b2b_to_flume.sh script, this converts comma, tab, or pipe delimited
files into JSON.


%prep
%setup -q

%check
export PYTHONPATH=agent/B2B
python test/B2B/%{name}_test.py

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d $RPM_BUILD_ROOT/%{_bindir}
install -m 755 agent/B2B/%{name}.py $RPM_BUILD_ROOT/%{_bindir}/%{name}.py

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{_bindir}/%{name}.py


%changelog
* Wed Dec 10 2014 Alan Brenner <alan.brenner@teradata.com> 2.2
- Error handling for input encoding, including a try of cp1252, if utf8 fails.
- Add support for reading from gzip and bzip2 files.
* Tue Dec  9 2014 Alan Brenner <alan.brenner@teradata.com> 2.1
- Remove dependency on b2b_to_flume, since it depends on this.
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Rework needed for the new directory structure
* Tue Oct 14 2014 Alan Brenner <alan.brenner@teradata.com> 1.1
- Initial RPM release
