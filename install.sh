#!/bin/sh

Install () {
    

    LOCATION="source/"

    echo "Beginning installation..."
    cd ${LOCATION}
    md5sum -c --quiet checksums.md5

    if  [ "$?" = "0" ]; then
        # installation begins here
        echo "Checksums OK."
        cd ..

        mkdir -p "${1}"
        chown $(logname): "${1}"

        if [ -e "${1}/res" ]; then
            cp -pvi ${LOCATION}* ${1}
        else
            cp -rpvi ${LOCATION}* ${1}
        fi

        case "$1" in
            /*) ABSOLUTE_PATH=""$1"codedict";;
            *) ABSOLUTE_PATH="$(pwd)/"$1"codedict";;
        esac


        EXECTEXT='#!/bin/sh \n \n'${ABSOLUTE_PATH}' $@'

        case "$3" in
            */) ABSOLUTE_PATH=""$1"codedict";;
            *) ABSOLUTE_PATH="$(pwd)/"$1"codedict";;
        esac

        echo "$EXECTEXT" > ${2}"codedict"
        chmod +x ${2}"codedict"

    else
        echo "Installation error - checksums didn't match."
        exit 1
    fi
}


if [ -e source/ ]; then

    INSTALLDIR=$1
    EXECUTABLEDIR=$2

    
    if [ ! $INSTALLDIR ]; then
        INSTALLDIR="./"
    fi

    if [ ! $EXECUTABLEDIR ]; then
        EXECUTABLEDIR="/usr/local/bin/"         
    fi

    case "$INSTALLDIR" in
        */) INSTALLDIR=$INSTALLDIR;;
        *) INSTALLDIR=$INSTALLDIR"/";;
    esac

    case "$EXECUTABLEDIR" in
        */) EXECUTABLEDIR=$EXECUTABLEDIR;;
        *) EXECUTABLEDIR=$EXECUTABLEDIR"/";;
    esac


    echo "\
Installing from source.\n\
All files will be placed into "\'$INSTALLDIR\'" .\n\
The actual executable will be placed into "\'$EXECUTABLEDIR\'" ."
    
    while true; do
        read -p "Do you wish to install this program? (y/n) " yn
        case $yn in
            [Yy]* ) Install $INSTALLDIR $EXECUTABLEDIR; break;;
            [Nn]* ) exit;;
            * ) echo "Please answer yes or no. (y/n) ";;
        esac
    done
    
else
    echo "Installation error - missing files."
    exit 
fi
