#Sublime Text 2 - Coffee Compile

This package allows you to compile some or all of your CoffeeScript right from the editor.
The JavaScript output will even have syntax highlighting!


##Usage

Just highlight some CoffeeScript code, right click and select the _Coffee Compile_ command.
To compile the whole file, don't highlight any text.

This package assumes that the _coffee_ command is on your path (it probably is). You can
configure an explicit path to _coffee_ in the settings file.


### Common Issues (especially on OSX)

#### OSError: [Errno 2] No such file or directory

This is happening because the plugin can't find `coffee` (or `coffee.cmd` on Windows). To fix this,
set the `coffee_path` to the executable's directory.

If you don't know where `coffee` is, run the following in your terminal: `dirname ``which coffee```

#### env: node: No such file or directory

This is happening because `coffee` can't find your `node` executable. To fix this, set the `node_path` setting
to the executable's directory.

If you don't know where `coffee` is, run the following in your terminal: `dirname ``which node```


## Install

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

## Screenshot
![CoffeeCompile Screenshot](http://i.imgur.com/2J49Q.png)