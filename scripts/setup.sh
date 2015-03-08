#!/bin/sh



if [ -e lib/md5_checksum.txt ]; then
	FILENUMBER=$(wc -l lib/md5_checksum.txt | cut -f1 -d" ")
	
	if [ $FILENUMBER != '13' ]; then
		echo "Installation error - missing files." 
		exit 1

	else
		HOMEDIR=$(eval echo ~${SUDO_USER})
		echo $HOMEDIR
		cd lib/
		if [ ! $(md5sum -c md5_checksum.txt --quiet | grep .) ]; then
			# installation begins here
			echo "Checksums OK."

			mkdir -p $HOMEDIR/proggen/codedict_test/

			cd ../
			cp -r lib/ $HOMEDIR/proggen/codedict_test/
			cp -r res/ $HOMEDIR/proggen/codedict_test/
			ln -s $HOMEDIR/proggen/codedict_test/lib/codedict /usr/local/bin/codedict
			echo "Installation finished"
			exit 0
		else
			echo "Installation error - checksums didn't match."
			exit 1
		fi
	fi
else
	echo "Installation error - checksums missing."
	exit 1
fi


	
