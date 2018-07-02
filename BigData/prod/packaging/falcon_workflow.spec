%define _hadoop /usr/bin/sudo -u hdfs /usr/bin/hadoop
%define fconf /etc/falcon/tasks
%define workf /apps/workflow/json_to_hive_and_archive

Name:           falcon_workflow
Version:        2.24
Release:        1%{?dist}
Summary:        Falcon configuration files for the production cluster.

Group:          falcon
License:        commercial
URL:            http://lm.com
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
#BuildRequires:  
Requires:       hadoop-client

%description
Configuration file defining the cluster for other falcon packages.


%prep
%setup -q

%check
export PYTHONPATH=admin/falcon
python test/Falcon/get_hive_names_test.py
python test/Falcon/get_json_names_test.py
python test/Falcon/get_json_to_hive_map_test.py


%install
rm -rf $RPM_BUILD_ROOT
install -m 755 -d $RPM_BUILD_ROOT/%{fconf}
install -m 755 admin/falcon/create_archive_directory.sh $RPM_BUILD_ROOT%{fconf}/create_archive_directory.sh
install -m 755 admin/falcon/create_hive_table.sh $RPM_BUILD_ROOT%{fconf}/create_hive_table.sh
install -m 755 admin/falcon/create_json_table.sh $RPM_BUILD_ROOT%{fconf}/create_json_table.sh
install -m 755 admin/falcon/delete_json_table.sh $RPM_BUILD_ROOT%{fconf}/delete_json_table.sh
install -m 755 -d $RPM_BUILD_ROOT%{_bindir}
install -m 755 admin/falcon/json_to_table.py $RPM_BUILD_ROOT%{fconf}/json_to_table.py
install -m 755 admin/falcon/json_to_table.sh $RPM_BUILD_ROOT%{fconf}/json_to_table.sh
install -m 755 admin/falcon/workflow.xml $RPM_BUILD_ROOT%{fconf}/workflow.xml
install -m 755 admin/falcon/get_hive_names.py $RPM_BUILD_ROOT%{fconf}/get_hive_names.py
install -m 755 admin/falcon/get_json_names.py $RPM_BUILD_ROOT%{fconf}/get_json_names.py
install -m 755 admin/falcon/get_json_to_hive_map.py $RPM_BUILD_ROOT%{fconf}/get_json_to_hive_map.py

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{fconf}/create_archive_directory.sh
%{fconf}/create_hive_table.sh
%{fconf}/create_json_table.sh
%{fconf}/delete_json_table.sh
%{fconf}/json_to_table.py
%{fconf}/json_to_table.sh
%{fconf}/workflow.xml
%{fconf}/get_hive_names.py
%{fconf}/get_json_names.py
%{fconf}/get_json_to_hive_map.py

%post
if `hadoop fs -test -e %{workf}` ; then
    %{_hadoop} fs -rm %{workf}/*
else
    %{_hadoop} fs -mkdir %{workf}
fi
%{_hadoop} fs -put %{fconf}/create_archive_directory.sh %{workf}
%{_hadoop} fs -put %{fconf}/create_hive_table.sh %{workf}
%{_hadoop} fs -put %{fconf}/create_json_table.sh %{workf}
%{_hadoop} fs -put %{fconf}/delete_json_table.sh %{workf}
%{_hadoop} fs -put %{fconf}/get_hive_names.py %{workf}
%{_hadoop} fs -put %{fconf}/get_json_names.py %{workf}
%{_hadoop} fs -put %{fconf}/get_json_to_hive_map.py %{workf}
%{_hadoop} fs -put %{fconf}/json_to_table.py %{workf}
%{_hadoop} fs -put %{fconf}/json_to_table.sh %{workf}
%{_hadoop} fs -put %{fconf}/workflow.xml %{workf}

%preun
%{_hadoop} fs -rm -r %{workf}


%changelog
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.24
- %% for a % when doing other replacements
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.23
- debug
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.22
- fi not if to end
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.21
- debug create_json_table.sh
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.20
- fix get_json_to_hive_map sending the args array
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.19
- get rid of get_names.py
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.18
- fix get_json_to_hive_map.py file name
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.17
- really fix new map file option name
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.16
- fix new map file option name
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.15
- Oozie did not like the shared library approach.
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.14
- args is a list, and we only need entry 0.
- Refactor to share code for handling bad characters and column name length.
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.13
- Force debuging for get_hive_names to help resolve an issue.
* Thu Dec 11 2014 Alan Brenner <alan.brenner@teradata.com> 2.12
- Oozie has to get the python scripts from HDFS.
* Wed Dec 10 2014 Alan Brenner <alan.brenner@teradata.com> 2.11
- Run python scripts from HDFS, not /usr/bin.
* Wed Dec 10 2014 Alan Brenner <alan.brenner@teradata.com> 2.10
- Split timestamps into a string column and a bigint column
- Handle longer than 30 character file names in columns--SAS does not like them.
* Mon Dec  8 2014 Alan Brenner <alan.brenner@teradata.com> 2.9
- looks like Vantage might have a % sign after what would otherwise be a double, so handle it
* Mon Dec  8 2014 Alan Brenner <alan.brenner@teradata.com> 2.8
- additional logging for data extraction error
* Sat Dec  6 2014 Alan Brenner <alan.brenner@teradata.com> 2.7
- quotes around the timestamp format
* Sat Dec  6 2014 Alan Brenner <alan.brenner@teradata.com> 2.6
- remove lack of date support from json_to_table
* Sat Dec  6 2014 Alan Brenner <alan.brenner@teradata.com> 2.5
- Skip history field declaration
* Sat Dec  6 2014 Alan Brenner <alan.brenner@teradata.com> 2.4
- Regex fixes.
* Thu Dec  4 2014 Alan Brenner <alan.brenner@teradata.com> 2.1
- Use RCFile for storage for SQL-H integration
* Tue Dec  2 2014 Alan Brenner <alan.brenner@teradata.com> 2.0
- Rework needed for the new directory structure
* Thu Nov 13 2014 Alan Brenner <alan.brenner@teradata.com> 1.0
- Initial RPM release
