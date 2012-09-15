#Sublime Text 2 - Coffee Compile

This package allows you to compile some or all of your CoffeeScript right from the editor.
The JavaScript output will even have syntax highlighting!

![CoffeeCompile Screenshot](http://i.imgur.com/2J49Q.png)


### Mountain Lions
There is a known issue with OSX 10.8.1 (i.e. the latest Mountain Lion). It should be fixed soon!
Please accept this kitten as a small token of apology:

![Kitten Bribe](http://cityrag.com/wp-content/uploads/2012/06/kitten-closeup-1.jpg)


##Install

### Package Control
Install the _CoffeeCompile_ package from [http://wbond.net/sublime_packages/package_control](Package Control).


### Manual

Clone this repository from your Sublime packages directory:

#### Linux
```
$ cd ~/.config/sublime-text-2/Packages
$ git clone https://github.com/surjikal/sublime-coffee-compile "Coffee Compile"
```

#### Macosx
```
$ cd "~/Library/Application Support/Sublime Text 2/Packages"
$ git clone https://github.com/surjikal/sublime-coffee-compile "Coffee Compile"
```

#### Windows (manual install untested)
```
$ cd "%APPDATA%\Sublime Text 2"
$ git clone https://github.com/surjikal/sublime-coffee-compile "Coffee Compile"
```


##Usage

Just highlight some CoffeeScript code, right click and select the _Coffee Compile_ command.
To compile the whole file, don't highlight any text.

This package assumes that the _coffee_ command is on your path (it probably is).
