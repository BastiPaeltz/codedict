# codedict

A command-line dictionary for the developer who likes it organized.

## What is it?

**codedict** is a little command line tool designed to be your personal dictionary for programming / developing. It is entirely up to you how to organize and arrange it. Lightweight, locally stored and easy to use, you can create your own *reference*, *documentation* or *dictionary* for development with codedict.   
  
  codedict defines *5 values* for every 'vocabulary' :  

  * The actual (programming) **language** - e.g. 'python'
 
  * The **problem** - What do you want to do? - 'adding element to a list' for instance
    
  * The **solution** - How do you accomplish that? - 'list.append(element)' for instance 
   
  * The **comment** - A place for further notes - You can note where you have found that command or remind yourself with 'VERY PERFORMANT!' or whatever you like.
     
  * And the **code** - Here is where you write your code examples (Note: this is only a suggestion, you can do whatever you want here.) Code is automatically brought up in your favorite editor so you can edit and view it where it is most comfortable.   
  
  The little 'add to list' is only the smallest and least beneficial thing you can do with codedict to make your life easier, since you can add anything up to complicated algorithms in code form to codedict. This way you have got everything together nicely at a central location. 
  
## How to use   
  
  There are 4 elementary commands:
  
  * codedict **-a for ADDING**  
    * Basic, interactive, self-explaining way to add content to your codedict - but not the fastest one.   

  * codedict **-f for FILE**
    * You can add a basically unlimited amount of content to your codedict reading from a file. Just follow the pattern within the file of beginning every new element with a '%' and following that up with 3 (problem, solution, comment in that order) texts, each enclosed by '|'. Specify a language. See the sample.jpeg how to possibly structure such a file.  

  * codedict **-c for CODE**
  	* This opens up your editor where you can either work on already existing content of your codedict or create completely new one. Up on registering a new language you will get prompted to enter a suffix for that language which will give you nice syntax highlighting in your editor. Save the file if you're done, exit your editor - and done.   

  * codedict **-d for DISPLAY**
  	* Displays content from your codedict. Either for a complete language or for only certain problems. When doing the latter, all problems *starting* with your input get matched (e.g. *'-d python foo'* matches the problem foo as well as foobar for the language python) 
    This way, you can structure your codedict nicely (see the sample.jpeg).
    The output gets printed nicely to console or to your editor in table form. Afterwards you can do further operations on your result, like updating the comment for example or editing the code.    

And the complete **usage pattern**:     
  codedict -d LANGUAGE [PROBLEM] [-e --cut --hline]  
  codedict -c LANGUAGE PROBLEM  
  codedict -f LANGUAGE PATH-TO-FILE [--code PROBLEM]    
  codedict -a   
  codedict LANGUAGE --suffix SUFFIX  
  codedict --editor EDITOR  
  codedict --wait (off | on)  
  codedict --line INTEGER    
  
## How to install
  Run the **install.sh** inside the install directory, it's usage is:  
  install.sh INSTALL_TYPE [INSTALL_DIR] [EXE_DIR]  

  **INSTALL_TYPE options**
  * frozen: Installs a frozen (compiled) version. This won't require a python interpreter installed on your system.
  * source: Installs a source (python) version. This will require a python interpreter installed on your system.

  *INSTALL_DIR and EXE_DIR*: You can specify a directory where the actual executable respectively the required libraries / source files will be placed. 


  *Not available for Windows yet.*  

## Troubleshooting / remaining options explained

* Code adding doesn't work with my editor. I immediately see "Nothing changed".  
This has something to do with editors behaving very differently in terms of how the executable gets invoked and how they deal with files they're currently working on. **Set '--wait' to 'on' to solve this.**

* What is this '--cut' feature, I dont get it.

One way to structure your codedict is by generic terms. Have a look at the 'sample.jpeg'. 'data types' and 'characteristics' generic type is 'lang'. So when you want to display all language features without the nasty 'lang' output in front of every row, you can specify --cut to do that.

* Fair enough. But what does '--code' do when adding from a file?

By default the content of the file will be parsed like described in the related section above. When '--cut' is set and a 'problem' is specified, the file's content will not be parsed but instead set as the code field (of that specified 'problem'). 

## License
  
*MIT*
