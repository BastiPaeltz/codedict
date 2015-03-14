# codedict

### A command-line dictionary for the developer who likes it organized.

## What is it and why is it useful?

**codedict** is a little command line tool designed to be your personal dictionary for programming / developing. It is entirely up to you how to organize and arrange it.   Lightweight, locally stored - your data are yours - and easy to use, you can create your own *reference*, *documentation* or *dictionary* for development with codedict in no time.   
  
    For every 'vocabulary' codedict defines 5 values:  

  * The actual (programming) **language** - 'python' for instance  
  * The **use case** - What do you want to do? - 'adding element to a list' for instance  
  * The **command** - How do you accomplish that? - 'list.append(element)' for instance  
  * The **comment** - A place for further notes - You can note here where you have found that command, link to online documentation or remind yourself with 'VERY PERFORMANT!' for instance.  
  * And the code - Here is where you write your code examples (Note: this is only a suggestion, you can do whatever you want here.) Code is automatically brought up in your favorite editor so you can edit and view it where it is most comfortable.   
  
  Our little 'add to list' is only the smallest and least beneficial thing you can do with codedict to make your life easier. Different use cases could be: TODODODODODODO     
  
## Show me how to use it!    
	There are 4 elementary commands:
  
  * codedict **-a for ADDING**  
    * Basic, self-explaining way to add content to your codedict - but not the fastest one.   

  * codedict **-f for FILE**
    * You can add a basically unlimited amount of content to your codedict reading from a file. Just follow the pattern within the file of beginning every new element with a '%' and following that up with 3 (use case, command, comment in that order) texts, each enclosed by '|'. Specify a language and off you go!  

  * codedict **-c for CODE**
  	* Get ready for code! This opens up your editor where you can either work on already existing content of your codedict or add completely new one. Up on 'creating' a new language you will get prompted to enter a suffix for that language which will give you nice syntax highlighting in your editor. Save the file if you want, exit your editor - and done.   

  * codedict **-d for DISPLAY**
  	* Displays content from your codedict. Either for a complete language or for only certain use cases, if you want. The output gets printed nicely to console or to your editor in table form. Afterwards you can do further operations on your result, like updating the comment for example or editing the code.  

And the complete **usage pattern**:   
    codedict -d <language> [<use_case>] [-e --cut --hline]  
    codedict -a   
    codedict -f <language> <path-to-file>    
    codedict -c <language> <use_case>  
  
## How can I install it?

## License
  
*MIT*