#!/bin/sh

# Install rpmdevtools first.

set -e


if [ ! -d $HOME/rpmbuild ]
then
    pushd $HOME
    rpmdev-setuptree
    popd
fi

setuprpm() {
    DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    ver=`grep Version ${pkg}.spec | cut -f2 -d: | sed -e 's/ *//'`
    files=''
    pushd ..
    dir=${pkg}-${ver}
    ln -s -f . $dir
    files="$dir/packaging/${pkg}.spec"
}

buildrpm() {
    #echo "files = $files"
    max=0
    for file in $files
    do
        epoch=`stat -c %Y $file`
        if [ $epoch -gt $max ]
        then
            max=$epoch
        fi
    done
    #echo "max = $max"
    rpm=$HOME/rpmbuild/RPMS/noarch/${pkg}-${ver}-1.el6.noarch.rpm
    #echo "rpm = $rpm"
    if [ -f $rpm ]
    then
        epoch=`stat -c %Y $rpm`
        #echo "stat = $epoch"
        if [ $epoch -gt $max ]
        then
            rm ${pkg}-${ver}
            popd
            continue
        fi
    fi
    tar -czhf $HOME/rpmbuild/SOURCES/${pkg}-${ver}.tar.gz $files
    rm ${pkg}-${ver}
    if [ -e test ]
    then
        rm test
    fi
    popd # pushd in setup()
    pushd $HOME/rpmbuild/SPECS
    ln -s -f $DIR/${pkg}.spec .
    rpmbuild -bb ${pkg}.spec
    popd
}

pushd dev/packaging
for pkg in flume_dev_edge flume_dev_agent falcon_dev_cluster
do
    setuprpm
    case $pkg in
        flume_dev_edge)
            files="$files $dir/edge/flume/flume.conf"
            ;;
        flume_dev_agent)
            files="$files $dir/agent/flume/flume.conf"
            ;;
        falcon_dev_cluster)
            files="$files $dir/admin/falcon/cluster.xml"
            ;;
        *)
            echo "unknown package $pkg"
        ;;
    esac
    buildrpm
done
popd

pushd prod/packaging
for pkg in api_client b2b_to_flume Bing Google delim_to_json \
    flume_prod_edge flume_prod_agent \
    falcon_workflow \
    falcon_prod_cluster \
    falcon_bankrate \
    falcon_bing_geog falcon_bing_keyword \
    falcon_google_geog falcon_google_keyword \
    falcon_omniture \
    falcon_optimedia \
    falcon_quinstreet \
    falcon_vantage
do
    setuprpm
    case $pkg in
        api_client)
            files="$files $dir/edge/API/${pkg}.sh"
            ;;
        Bing)
            # bing.ini is intentionally not packaged
            ln -s -f ../test .
            files="$files $dir/edge/API/${pkg}.py"
            files="$files $dir/test/API/${pkg}_test.py"
            ;;
        Google)
            #  google.yaml is intentionally not packaged
            ln -s -f ../test .
            files="$files $dir/edge/API/${pkg}.py"
            files="$files $dir/test/API/${pkg}_test.py"
            ;;              
        b2b_to_flume)
            files="$files $dir/agent/B2B/${pkg}.sh"
            ;;
        delim_to_json)
            ln -s -f ../test .
            files="$files $dir/agent/B2B/${pkg}.py"
            files="$files $dir/test/B2B/${pkg}_test.py"
            ;;
        flume_prod_edge)
            files="$files $dir/edge/flume/flume.conf"
            ;;
        flume_prod_agent)
            files="$files $dir/agent/flume/flume.conf"
            ;;
        falcon_workflow)
            pth=$dir/admin/falcon
            files="$files $pth/create_archive_directory.sh"
            files="$files $pth/create_hive_table.sh"
            files="$files $pth/create_json_table.sh"
            files="$files $pth/delete_json_table.sh"
            files="$files $pth/json_to_table.sh"
            files="$files $pth/json_to_table.py"
            files="$files $pth/workflow.xml"
            files="$files $pth/get_json_names.py"
            files="$files $pth/get_hive_names.py"
            files="$files $pth/get_json_to_hive_map.py"
            files="$files $dir/test/Falcon/get_json_names_test.py"
            files="$files $dir/test/Falcon/get_hive_names_test.py"
            files="$files $dir/test/Falcon/get_json_to_hive_map_test.py"
            files="$files $dir/test/Falcon/test_map_csv.txt"
            files="$files $dir/test/Falcon/test_map_tsv.txt"
            ;;
        falcon_prod_cluster)
            files="$files $dir/admin/falcon/cluster.xml"
            ;;
        falcon_*)
            pth=$dir/admin/falcon
            src=`echo $pkg | /bin/cut -s -f 2- -d _`
            files="$files $pth/archive_${src}.xml"
            files="$files $pth/lz_${src}.xml"
            files="$files $pth/process_${src}.xml"
            ;;        
        *)
            echo "unknown package $pkg"
        ;;
    esac
    buildrpm
done
