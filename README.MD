# Coding encyclopedia
  
Ein command line tool für Developer zum Aufbauen einer Enzyklopädie fürs Programmieren
## Was ist es  
  
###Skip am besten gleich zu "Usage"

Ein command line tool, das Programmierern die Möglichkeit bietet ihre eigene Documentation zu schreiben, ganz wie sie es wollen.
Gut, das sagt noch gar nix aus und beschreibt es eigentlich auch nicht 100 %, an einem Bsp. wird deutlicher was ich will:  
  
Häufig googlet man nach "wie mache ich $DING in $Programmiersprache" und landet dann wahlweise auf stackoverflow, der Sprachen-Documentation, auf Tutorialseiten oder ähnlichem.   

Die Idee meines Projekts ist es, dass der Programmierer sich das "Gelernte" selbst organisieren und in seiner eigenen Encyclopädie speichern und nach Belieben darauf zugreifen kann. Ob recommended best Practices, seine eigenen Vorlieben, wie und womit er $DING löst oder nur kurze Anmerkungen, die er sich macht. Aber damit nicht genug, ich will dass es noch mehr gibt, aber dazu später mehr.  
  
## Usage   
  
ce language [use_case] [-s -a]   
  
ODER  
  
ce add [-I -i]  
  

####Was es tut:
Ich fang Verständlichkeitshalber mit "ce add" an:  
  
ce add -> Man wird aufgefordert mit entsprechenden Prompts folgendes einzugeben:
Hier ein Besipiel  
  				
language:	        python  
use_case: 	increment  
command: 	+= 1  
comment:	"NIE i=i+1 benutzen"  
alternatives:	none  
links:		link_zur_documentation, (oder zb. link zu einer frage bei stack overflow die wichtig ist und damit zu tun hat)  
code examples:	[
					i = 0     
					i += 1  
					# output i = 1  
				]

Gibt man "quit()" ein, während der Bearbeitung bleiben die restlichen Felder leer.  

-I -> gibt die Möglichkeit nur ein einzelnes "Feld" zu ändern,also zb.  

ce add -I python:increment:comment ",NIEMALS!"
  
-i -> selbes wie i aber überschreibt den Inhalt des Feldes  
  


Nun zu ce language:
  

ce language -> gibt einem (am besten in einem HTML doc) alle gesetzten use_cases usw. aus, z.B.

ce ruby 

  
ce language use_case gibt einem den command für den gesetzten use_case aus:
  
ce javascript output -> gibt z.B. "console.log()"  

Will man mehr haben gibt es die Flags -s(short, gibt zusätzlich noch den comment aus) und -a(all)

ce javascript output -s -> "console.log()", "Semikolon am Ende nicht vergessen"

ce javascript output -a ->

command: 	console.log  
comment:	"Semikolon nicht vergessen"    
alternatives:	  none  
links:		"http://www.w3schools.com/js/js_output.asp",   "http://www.weblizards.de/blog/2012/01/javascript-debuggen-mit-console-log-verfeinert/"  
code examples:	[
					console.log("A")  
					// output A
					console.log(1+2)
					//output 3  
				]  


Das war erstma die Basic-Version. Ich hab noch so einige Ideen für Features und Verfeinerungen. 

## Wilde Ideen
Da kann man noch soo viel machen. Meine Ideen z.B. noch dass man comments oder links als important flaggen kann, sodass sie IMMER mit angezeigt werden. Oder dass man Links gewichten kann, wenn man will.  Und wenn ich das ganz weit spinne: Wenn man das online gibt, können Developer über die commands diskutieren und sie use_cases zuordnen und up oder downvoten. Und wenn genug upvotes zusammenkommen, werden sie als Standard dafür gesetzt und sind dann für jedermann nachlesbar. Wenn bestimmte commands viele downvotes bekommen und der User versucht bei sich einen use_case mit diesem command anzulegen, kriegt er einen Warnhinweis. Oder wenn ein command deprecated ist, bekommt er einen Hinweis.    

##Aber die Basic Idee bleibt immer noch:

Man selbst denkt nie so, wie es einen documentation tut. Und schon gar nicht wie es viele davon tun. 

Man kann also 1. sich die keywords (use_cases) so wählen wie man es selbst will, sie in seinem Gehirn so danach sortieren wie man halt denkt. Außerdem kann man sich so über die Jahre einen Wissensvorrat für sich selbst anlegen, der immer nur stetig größer wird. Wie mache ich das und das in der und der Sprache, alles gebündelt in einer appplikation, die man durch wenige keystrokes aufrufen kann. Und gleichzeitig kann man sie jederzeit nach seinem Belieben ändern. Ach mann ich kann gar nich genug sagen wie geil ich diese Idee einfach finde. Wahrscheinlich ist sie in meinem Kopf tausend mal geiler als ich es hier beschreiben konnte (oder als sie ist) :D

## Wie sieht die Implementierung aus
das dürfte eig sehr machbar sein, eine lokale DB für die ganzen Daten, eine command line applikation in python ruby oder so und HTML um die Inhalte der DB schön anzuzeigen erstmal. Später dann ne Website wenn wir es auch für andere anbieten wollen (ursprünglich hatte ich das mir nur für mich selbst gedacht). Also echt nich so viel!