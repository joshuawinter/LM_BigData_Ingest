Name:           flume_dev_agent
Version:        2.0
Release:        1%{?dist}
Summary:        Flume configuration files for dev agent nodes.

Group:          flume
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       flume

%description
Configuration files to move data to HDFS.


%prep
%setup -q

%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d $RPM_BUILD_ROOT/etc/flume/conf
install -m 755 agent/flume/flume.conf $RPM_BUILD_ROOT/etc/flume/conf/%{name}.conf

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
/etc/flume/conf/%{name}.conf

%post
if [ -f /etc/flume/conf/flume.conf -a ! -f /etc/flume.conf/flume_orig.conf ]
then
	mv /etc/flume/conf/flume.conf /etc/flume/conf/flume_orig.conf
fi
ln -s %{name}.conf /etc/flume/conf/flume.conf

%postun
if [ -f /etc/flume/conf/flume_orig.conf ]
then
	mv /etc/flume/conf/flume_orig.conf /etc/flume/conf/flume.conf
fi


%changelog
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Rework needed for the new directory structure
* Fri Oct 17 2014 Alan Brenner <alan.brenner@teradata.com> 1.2
- Handle overriding existing conf file.
* Thu Oct 16 2014 Alan Brenner <alan.brenner@teradata.com> 1.0
- Initial RPM release
