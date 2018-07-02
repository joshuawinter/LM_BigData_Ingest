Name:           api_client
Version:        2.4
Release:        1%{?dist}
Summary:        Cron job to run Bing.py and other API clients

Group:          B2B
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       Bing, Google, cronie, wget

%description
The api_client.sh script runs the Bing.py and Google.py programs to extract
reporting data into JSON, and then push that json file to a flume directory,
or wget for sources that can provide data in JSON directly from a URL.


%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/LM
install -m 755 -d $RPM_BUILD_ROOT/%{_bindir}
install -m 755 edge/API/%{name}.sh $RPM_BUILD_ROOT%{_bindir}/%{name}.sh

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{_sysconfdir}/LM
%{_bindir}/%{name}.sh


%changelog
* Tue Dec  9 2014 Alan Brenner <alan.brenner@teradata.com> 2.4
- John found a bug with Bing (need to specify -u to use pycurl, not liburl).
* Tue Dec  9 2014 Alan Brenner <alan.brenner@teradata.com> 2.3
- MediaAlpha update.
* Mon Dec  8 2014 Alan Brenner <alan.brenner@teradata.com> 2.2
- Correct temporary directory naming.
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.1
- Rework needed for the new directory structure
* Wed Nov  5 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Add support for MediaAlpha extracts via wget.
* Wed Oct 29 2014 Alan Brenner <alan.brenner@teradata.com> 1.7
- Google needs hand-holding.
* Tue Oct 21 2014 Alan Brenner <alan.brenner@teradata.com> 1.6
- Remove invalid -p switch from call to Google (still needed for Bing).
* Fri Oct 17 2014 Alan Brenner <alan.brenner@teradata.com> 1.5
- Fix t parameter, other bugs.
* Tue Oct 15 2014 Alan Brenner <alan.brenner@teradata.com> 1.0
- Initial RPM release
