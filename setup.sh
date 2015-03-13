#!/bin/sh

Install () {
	
	# $1 INSTALLTYPE $2 INSTALLDIR $3 EXEDIR
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

		if [ -e ]

		if [ -e $(pwd)$LOCATION ]; then
			cp -rv ${LOCATION} ${2}
		else
			exit 1
		fi

		if [ "$2" = "*/" ]; then
			if [ ! "$2" = "/*" ]; then
				# relative location, ending-'/' trailed
				ABSOLUTE_PATH="$(pwd)/"$2"/"$LOCATION"codedict"
			else
				ABSOLUTE_PATH=""$2""$LOCATION"codedict"
			fi
		else
			if [ ! "$2" = "/*" ]; then
				# relative location, no ending '/'
				ABSOLUTE_PATH="$(pwd)/"$2""$LOCATION"codedict"
			else
				ABSOLUTE_PATH=""$2"/"$LOCATION"codedict"
			fi
		fi

		chown "$(logname)" ${ABSOLUTE_PATH%"codedict"}
		chmod 755 $ABSOLUTE_PATH
		chmod 755 ${ABSOLUTE_PATH%"codedict"}


		EXECTEXT='#!/bin/sh \n \n'$ABSOLUTE_PATH' $@'

		if [ "$3" = "*/" ]; then 
			sudo echo "$EXECTEXT" > ${3}"codedict" 
			chmod +x ${3}"codedict"
		else
			sudo echo "$EXECTEXT" > ${3}"/codedict"
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
			INSTALLDIR="./"
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

