#!/bin/sh

Install () {
	
	# $1 INSTALLTYPE $2 INSTALLDIR $3 EXEDIR
	if [ $1 = '1' ]; then
		LOCATION="general_installation/"
	else
		LOCATION="python_installation/"
	fi

	cd ${LOCATION}

	if [ ! $(md5sum -c checksum.txt | grep md5sum) ]; then
		# installation begins here
		echo "Checksums OK."
		cd ..

		if [ -e "${2}/res" ]; then
			cp -pvi ${LOCATION}* ${2}
		else
			cp -rpvi ${LOCATION}* ${2}
		fi

		case "$2" in
		    /*) ABSOLUTE_PATH=""$2"codedict";;
		    *) ABSOLUTE_PATH="$(pwd)/"$2"codedict";;
		esac


		EXECTEXT='#!/bin/sh \n \n'$ABSOLUTE_PATH' $@'

		case "$3" in
		    */) ABSOLUTE_PATH=""$2"codedict";;
		    *) ABSOLUTE_PATH="$(pwd)/"$2"codedict";;
		esac

		echo "$EXECTEXT" > ${3}"codedict"
		chmod +x ${3}"codedict"

	else
		echo "Installation error - checksums didn't match."
		exit 1
	fi
}


if [ -e src_installation/ -a -e frozen_installation/ ]; then

	INSTALLTYPE=$1
	INSTALLDIR=$2
	EXECUTABLEDIR=$3

	if [ "$INSTALLTYPE" != "1" -a "$INSTALLTYPE" != "2" ]; then
		echo "\
Please enter a correct installation type.\n\
Installation types:\n\
1: Frozen installation - upside: No interpreter required. - downside: executable is compiled.\n\
2: Source installation - upside: source code is readable. - downside: Python 2.7 interpreter required.\n\
If you are uncertain if the compiled file is malicious test it with antivirus software \n\
or try to get reviews from people who already used it. \n\
Do your research - you shouldn't trust me blindly."
		exit

	else
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

		if [ $INSTALLTYPE = '1' ]; then
			INSTALLTEXT="frozen"
		else
			INSTALLTEXT="source"
		fi

		echo "\
You selected "$INSTALLTEXT" installation.\n\
All files will be placed into "$INSTALLDIR".\n\
The actual executable will be placed into "$EXECUTABLEDIR"."
		
		while true; do
		    read -p "Do you wish to install this program? (y/n) " yn
		    case $yn in
		        [Yy]* ) Install $INSTALLTYPE $INSTALLDIR $EXECUTABLEDIR; break;;
		        [Nn]* ) exit;;
		        * ) echo "Please answer yes or no. (y/n) ";;
		    esac
		done
	fi
else
	echo "Installation error - missing files."
	exit 
fi

