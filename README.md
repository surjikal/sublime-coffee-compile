# Sublime Text 2/3 - Coffee Compile

This package allows you to compile some or all of your CoffeeScript right from the editor.
The JavaScript output will even have syntax highlighting!

To install CoffeeCompile, simply use [Package Control](http://wbond.net/sublime_packages/package_control).

You'll need to setup some paths in the settings file before you can use the plugin. Instructions are
included in the settings file, don't worry! The settings file can be accessed through this menu:
`Sublime Text > Preferences > Package Settings > CoffeeCompile > Settings - User`

To use the plugin, highlight your CoffeeScript and hit `Ctrl+Shift+C` (or `Cmd+Shift+C` on OSX).<br>
Alternatively, right click and select the _Coffee Compile_ command. To compile the whole file, don't
highlight any text.


![CoffeeCompile Screenshot](http://i.imgur.com/2J49Q.png)

Color Scheme: [Made of Code](http://madeofcode.com/posts/29-photo-my-new-textmate-theme-8220-made-of-code-8221-mdash-download-9-feb-2010-update-t)

## Common Issues

### OSError: [Errno 2] No such file or directory

This is happening because the plugin can't find `coffee` (or `coffee.cmd` on Windows). To fix this,
go in the settings file and set the `coffee_path` to the executable's directory.

If you don't know where `coffee` is, run the following in your terminal: ``dirname `which coffee` ``

### env: node: No such file or directory

This is happening because `coffee` can't find your `node` executable. To fix this, go in the settings
file and set the `node_path` setting to the executable's directory.

If you don't know where `node` is, run the following in your terminal: ``dirname `which node` ``


## Install

### Package Control
Install the _CoffeeCompile_ package from [Package Control](http://wbond.net/sublime_packages/package_control).


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
