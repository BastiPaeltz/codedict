# codedict

#### A command-line dictionary for the developer who likes it organized.

#### Thanks to <a href="https://github.com/adamnew123456">Adam</a> for his awesome pull request which brings export and import functionality to codedict.

## What is it?

**codedict** is a little command line tool designed to be your personal dictionary for programming / developing. It is entirely up to you how to organize and arrange it.  
**Lightweight and locally stored**, you can create your own *reference*, *documentation* or *dictionary* for development with codedict.

codedict uses the **classic Cookbook** approach and adds additonal tag features. A typical **codedict entry** consists of 4 values: 

  * (programming) **language** - e.g. *'python'*

  * **tags**, seperated by semicolon - e.g. *'list methods;lists'*
 
  * **problem** - *What do you want to do?* - *'adding element to a list'* for instance
    
  * The **solution** - *How do you accomplish that?* - *'list.append(element)'* for instance.  
  solution can be anything, from complicated algorithms or code examples to simple one-liners like our add-to-list example since you can **edit inside your favorite editor, where it is most comfortable.**
  
## How to use   
  
  Here are the elementary commands:
  
  * `codedict add` 
    * Basic, interactive, self-explaining way to **add content** to your codedict. 
  
  * `codedict tags`
    * Lists **all tags** for the given language and offers to display **all entries associated** with a certain tag.
  
  * `codedict edit`
    * A shortcut for adding or **editing content**. You need to provide a language as well as a problem. If this combination already exists, you can edit the already exisiting solution. If not, a **new entry will be created**. 

  * `codedict file`
    * You can add a basically **unlimited amount of content** to your codedict **at a time** by reading from a file. Just follow the pattern of beginning every new element(vocabulary) with a '%' and following that up with 3 (tags, problem, solution in that order) sections, each enclosed by '|'. See the **sample.png for an example**.   
    Content gets **overwritten** when adding new entries. So in case you messed something up - *codedict rollback im sure* will bring you to the point right before your last adding from file. 

  * `codedict display`
    * Displays content from your codedict. Either for an **entire language** or only for certain problems, which match the **search pattern**. When doing the latter, all problems *starting* with your input get matched (e.g. *'python foo'* matches the problem *foo* as well as *foobar* for the language python).     
    The output gets printed to **console** (if it isn't longer than 25 lines), to your **pager** or editor in **table form**. Afterwards you can do **further operations**, like updating the solution for example. See the section below for more information.

  * `codedict link` 
    * You can add links to your codedict. Provide an **URL**, give it a name (optionally, but recommended) and assign it to a certain language (optionally).

  * `codedict export file language` and `codedict import file`
    * codedict allows you to export and import entries stored outside of your database for easy backup and storage.

**When in doubt - `codedict -h` brings you to the help page.**


## How to install
  Clone the current revision of the repository with  
  `git clone --depth=1  https://github.com/BastiPaeltz/codedict.git`

  Run the **install.sh** inside the install directory, it's **usage** is:  
  `install.sh [INSTALL_DIR] [EXE_DIR]`  

*INSTALL_DIR* and *EXE_DIR*:  
 You can specify a directory where the actual executable respectively the required libraries / source files **will be placed**. You **won't require** `sudo` rights to install if neither of those directories is in root land. 
  
**Requires python 2.7 interpreter**   
  
### codedict on Windows

I tested codedict on Windows and the **core program works** on Windows shells (PowerShell etc.) and unix shells (git bash etc.). Just clone codedict and `cd` into the `source` folder. On Windows shells, you would run `python.exe codedict`, on unix shells just run `./codedict`.   
The **problem** is, I'm not a Windows guy and unfortunately have no clue how to make codedict runnable from anywhere.  
**It would be supercool, if someone of you, who knows how to work with Windows could help me out with this.**  

## Troubleshooting / remaining options explained

* After displaying my table, I get prompted with:   
`'Do you want to do more? Usage: INDEX [ATTRIBUTE] - Press ENTER to abort:'` 

*Based on the table you can edit your codedict this way.* **Choose the entry you want to change by index.** *If you omit the attribute, you will be brought to your editor (for normal tables), where you can edit the solution - or for link tables, your browser will be opened on the entrie's URL*.  
ATTRIBUTE can be `problem` or `tags` for normal tables and  
`name` or `language` for link tables.  
**You can also type `del`, if you want to delete an entry entirely.**

* codedict doesn't work with my editor. **I immediately see "Nothing changed"**.
*This has something to do with editors behaving differently in terms of how their executable gets invoked and how they deal with files they're currently working on.*  
**Set `--wait` to 'on' to solve this.** 

* `codedict display` has a `-l` and a `-t` option.

*-l displays* **links** *in the same way like normal display does with dictionary entries. -t works a bit differently. It won't display tags (thats what `codedict tags` is for), but display all (dict) entries that match the pattern.*

* `codedict display "" "my_search_pattern"`

*One extra trick you can do - if you omit the language like above, entries get matched across languages. The command above would display all 'my_search_pattern' entries, no matter what language.*

* What happens when I set `problem` additionally when adding from a file ?

*By default the content of the file will be parsed like described in the related section above. When 'problem' is set, the file's content will not be parsed but instead set as the* `solution` field *(of that specified 'problem').* 

* How can I see my current configurations (editor etc.) ?

*Just invoke the command you like without a value - e.g.* `codedict --editor`

## Shell auto completion
There are completion files provided for **zsh and bash** inside the shell completion folder.


## License
  
*MIT*
