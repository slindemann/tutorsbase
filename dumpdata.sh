#!/usr/bin/env bash

DATABASENAME="" # "tb_25Feb"
DOCKER="" # "tutorsbase_postgres_1"
DB_DUMP_FOLDER="db_saves"


USER="postgres"

DUMP_OPTIONS=("--data-only"
         "--column-inserts")

TABLES=("auth_user"
        "student_crediting_exgroup"
        "student_crediting_student"
        "student_crediting_sheet"
        "student_crediting_exercise"
        "student_crediting_result"
        "student_crediting_presence"
        "student_crediting_exam"
        "student_crediting_examexercise"
        "student_crediting_exampresence"
        "student_crediting_examresult"
        "student_crediting_config")

LIST_OF_TABLES+=""

COMMAND=""


dumpdata()
{
    for ((i=0;i<${#TABLES[@]};i++)) 
    do
        LIST_OF_TABLES+="-t ${TABLES[i]} "
    done
    #docker exec -t tutorsbase_postgres_1 pg_dump --column-inserts --data-only -U postgres -t auth_user -t student_crediting_exgroup -t student_crediting_student -t student_crediting_sheet -t student_crediting_exercise -t student_crediting_result -t student_crediting_presence -t student_crediting_exam -t student_crediting_examexercise -t student_crediting_exampresence -t student_crediting_examresult -t student_crediting_config -d DATABASENAME > db_save_`date +%Y%m%d"_"%H%M`.sql
    COMMAND="docker exec -t ${DOCKER} pg_dump ${DUMP_OPTIONS[@]} -U ${USER} ${LIST_OF_TABLES} -d ${DATABASENAME} > ${DB_DUMP_FOLDER}/db_save_`date +%Y%m%d"_"%H%M`.sql"
    #echo "$COMMAND"
    eval "$COMMAND"
}


usage()
{
    echo "usage: dumpdata.sh -d/--database DATABASENAME -D/--docker DOCKER [-F/--folder DB_DUMP_FOLDER]"
    echo "       e.g., 'dumpdata.sh -d tb_25Feb -D tutorsbase_postgres_1'"
}



##### Main



while [[ "$1" =~ ^- && ! "$1" == "--" ]]; do case $1 in
  -d | --database )
    shift; DATABASENAME=$1
    ;;
  -D | --docker )
    shift; DOCKER=$1
    ;;
  -F | --folder )
    shift; DB_DUMP_FOLDER=$1
    ;;
  -h | --help )
    usage; return 1
    ;;
esac; shift; done
if [[ "$1" == '--' ]]; then shift; fi
if [[ -z "$DATABASENAME" ]] || [[ -z "$DOCKER" ]]; then
    echo "Database and/or Docker-container not specified!"
    usage
    return 1
fi
dumpdata
