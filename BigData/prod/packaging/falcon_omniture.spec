%define falcon_url http://localhost:15000/
%define _falcon /usr/bin/sudo -u hdfs /usr/bin/falcon
%define gname omniture
%define fconf /etc/falcon/tasks
%define _grep /bin/grep
%define _cut /usr/bin/cut
%define _date /bin/date
%define _sed /bin/sed

Name:           falcon_%{gname}
Version:        2.1
Release:        1%{?dist}
Summary:        Falcon configuration files for the production cluster.

Group:          falcon
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       falcon_cluster, falcon_workflow, grep, coreutils

%description
Configuration file defining the cluster for other falcon packages.


%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d $RPM_BUILD_ROOT%{fconf}
install -m 644 admin/falcon/archive_%{gname}.xml $RPM_BUILD_ROOT%{fconf}/archive_%{gname}.xml
install -m 644 admin/falcon/lz_%{gname}.xml $RPM_BUILD_ROOT%{fconf}/lz_%{gname}.xml
install -m 644 admin/falcon/process_%{gname}.xml $RPM_BUILD_ROOT%{fconf}/process_%{gname}.xml

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{fconf}/archive_%{gname}.xml
%{fconf}/lz_%{gname}.xml
%{fconf}/process_%{gname}.xml

%post
%{_falcon} entity -url %{falcon_url} -type feed -file %{fconf}/archive_%{gname}.xml -submitAndSchedule
%{_falcon} entity -url %{falcon_url} -type feed -file %{fconf}/lz_%{gname}.xml -submitAndSchedule
%{_sed} -s -i "s/validity start=\"20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]/validity start=\"`%{_date} +%Y-%m-%d`/" %{fconf}/process_%{gname}.xml
%{_falcon} entity -url %{falcon_url} -type process -file %{fconf}/process_%{gname}.xml -submitAndSchedule

%preun
%{_falcon} entity -url %{falcon_url} -type process -name `%{_grep} process %{fconf}/process_%{gname}.xml | %{_grep} name | %{_cut} -f4 -d'"'` -delete
%{_falcon} entity -url %{falcon_url} -type feed -name `%{_grep} feed %{fconf}/archive_%{gname}.xml | %{_grep} name | %{_cut} -f4 -d'"'` -delete
%{_falcon} entity -url %{falcon_url} -type feed -name `%{_grep} feed %{fconf}/lz_%{gname}.xml | %{_grep} name | %{_cut} -f4 -d'"'` -delete

%changelog
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Rework needed for the new directory structure
* Mon Nov 17 2014 Alan Brenner <alan.brenner@teradata.com> 1.0
- Initial RPM release