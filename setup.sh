#!/bin/sh

Install () {
	
	if [ $1 = '1' ]; then
		LOCATION="default_installation/"
	else
		LOCATION="python_installation/"
	fi

	cd ${LOCATION}

	if [ ! $(md5sum -c checksum.txt --quiet) ]; then
		# installation begins here
		echo "Checksums OK."
		cd ..

		cp -rv ${LOCATION} ${2}

		if [ "$2" = "*/" ]; then
			ABSOLUTE_PATH="$(pwd)/"$2"/"$LOCATION"codedict_run"
		else
			ABSOLUTE_PATH="$(pwd)/"$2""$LOCATION"codedict_run"
		fi

		echo $ABSOLUTE_PATH

		EXECTEXT='#!/bin/sh \n \n'$ABSOLUTE_PATH' $@'

		if [ "$3" = "*/" ]; then 
			echo "$EXECTEXT" > ${3}"codedict" 
			chmod +x ${3}"codedict"
		else
			echo "$EXECTEXT" > ${3}"/codedict"
			chmod +x ${3}"/codedict"
		fi


	else
		echo "Installation error - checksums didn't match."
		exit 1
	fi
}




if [ -e python_installation/checksum.txt ]; then

	INSTALLTYPE=$1
	INSTALLDIR=$2
	EXECUTABLEDIR=$3

	if [ "$INSTALLTYPE" != "1" -a "$INSTALLTYPE" != "2" ]; then
		echo "\
Please enter a correct installation type.\n\
Installation types:\n\
1: Default installation - upside: Nothing required - downside: executable is compiled.\n\
2: Python installation - upside: source code is readable. downside: Python 2.7 Interpreter required."
		exit
	else
		if [ ! $INSTALLDIR ]; then
			INSTALLDIR=$(pwd)
		fi

		if [ ! $EXECUTABLEDIR ]; then
			EXECUTABLEDIR="/usr/local/bin/"
		fi

		if [ $INSTALLTYPE = '1' ]; then
			INSTALLTEXT="Default"
		else
			INSTALLTEXT="Python"
		fi

		echo "\
You selected "$INSTALLTEXT" installation\n\
All files will be placed into "$INSTALLDIR"\n\
The actual executable (that you will run from the command line) will be placed into "$EXECUTABLEDIR""
		
		while true; do
		    read -p "Do you wish to install this program? " yn
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

