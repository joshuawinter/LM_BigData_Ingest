%define falcon_url http://localhost:15000/
%define _falcon /usr/bin/sudo -u hdfs /usr/bin/falcon
%define gname cluster
%define fconf /etc/falcon/tasks
%define _grep /bin/grep
%define _sed /bin/sed

Name:           falcon_dev_%{gname}
Provides:       falcon_%{gname}
Version:        2.0
Release:        1%{?dist}
Summary:        Falcon configuration files for the non-production cluster.

Group:          falcon
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       falcon, grep, sed, falcon_workflow

%description
Configuration file defining the cluster for other falcon packages.


%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d $RPM_BUILD_ROOT%{fconf}
install -m 755 admin/falcon/cluster.xml $RPM_BUILD_ROOT%{fconf}/cluster.xml

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{fconf}
%{fconf}/cluster.xml

%post
%{_falcon} entity -url %{falcon_url} -type cluster -file %{fconf}/cluster.xml -submit

%preun
%{_falcon} entity -url %{falcon_url} -type cluster -name `%{_grep} cluster %{fconf}/cluster.xml | %{_sed} -ne 's/.*name="\([^"]*\)".*/\1/p'` -delete


%changelog
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Rework needed for the new directory structure
* Thu Nov  13 2014 Alan Brenner <alan.brenner@teradata.com> 1.0
- Initial RPM release
