#!/bin/sh

hadoop fs -rm /apps/workflow/json_to_hive_and_archive/*
hadoop fs -put cr*.sh d*.sh j*.sh *.py workflow.xml /apps/workflow/json_to_hive_and_archive
hadoop fs -ls /apps/workflow/json_to_hive_and_archive
