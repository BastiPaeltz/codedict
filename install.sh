#!/bin/sh

Install () {
	
	# $1 INSTALLTYPE $2 INSTALLDIR $3 EXEDIR
	if [ $1 = '1' ]; then
		LOCATION="general_installation/"
	else
		LOCATION="python_installation/"
	fi

	cd ${LOCATION}
	echo $3

	if [ ! $(md5sum -c checksum.txt --quiet) ]; then
		# installation begins here
		echo "Checksums OK."
		cd ..

		if [ -e "${2}/res" ]; then
			cp -pv ${LOCATION}* ${2}
		else
			cp -rpv ${LOCATION}* ${2}
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


if [ -e python_installation/codedict -o -e general_installation/codedict ]; then

	INSTALLTYPE=$1
	INSTALLDIR=$2
	EXECUTABLEDIR=$3

	if [ "$INSTALLTYPE" != "1" -a "$INSTALLTYPE" != "2" ]; then
		echo "\
Please enter a correct installation type.\n\
Installation types:\n\
1: General installation - upside: No Interpreter required - downside: executable is compiled.\n\
2: Python installation - upside: source code is readable. downside: Python 2.7 Interpreter required.\n\
If you are uncertain if the compiled file is malicious test it with antivirus software \n\
or try to get reviews from people who already tried it. \n\
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
			INSTALLTEXT="General"
		else
			INSTALLTEXT="Python"
		fi

		echo "\
You selected "$INSTALLTEXT" installation\n\
All files will be placed into "$INSTALLDIR"\n\
The actual executable (that you will run from the command line) will be placed into "$EXECUTABLEDIR""
		
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
	exit 1
fi

