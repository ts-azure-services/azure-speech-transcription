#!/bin/bash
#Script to show cognitive service list kinds
grn=$'\e[1;32m'
end=$'\e[0m'

list_kinds=$(az cognitiveservices account list-kinds)
printf "${grn}COGNITIVE SERVICE KINDS \n $list_kinds ${end}\n"
