#!/bin/sh


if [ -e lib/lib_checksum.txt -a -e codedict_checksum.txt -a -e codedict ]; then
	FILENUMBER=$(wc -l lib/lib_checksum.txt | cut -f1 -d" ")
	
	if [ $FILENUMBER != '18' ]; then
		echo "Installation error - missing required files." 
		exit 1

	else
		if [ ! $(md5sum -c lib/lib_checksum.txt --quiet) -a  \
			! $(md5sum -c codedict_checksum.txt --quiet) ]; then
			# installation begins here
			echo "Checksums OK."

			mkdir -pv /usr/share/codedict/
			chmod o+w /usr/share/codedict
			cp -rv lib/ usr/share/codedict/
			cp -v codedict /usr/local/bin/
			echo "Installation finished"
			exit 0
		else
			echo "Installation error - checksums didn't match."
			exit 1
		fi
	fi
else
	echo "Installation error - checksums missing or executable not in place."
	exit 1
fi


	
