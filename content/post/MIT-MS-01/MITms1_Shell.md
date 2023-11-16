+++
title = 'MITMS01_课程概述与Shell'
date = 2023-11-02 16:43:23+0800 
draft = false
math = true
summary = "MIT Missing Semester 1, Course overview and the shell"
categories:
    - 学习笔记
    - CS
tags:
    - MIT Missing Semester
    - Shell
+++
打开终端如下图

![Alt text](Pasted%20image%2020231102192205.png)

其告诉你：你的用户名为Azusaislit，主机名为Roboride-Portab

运行 date 程序，显示出当前时间

可以在执行运行程序的命令的同时传递参数，比如运行 echo 程序的同时传递参数 Hello，这将会在你的终端输出 Hello

![Alt text](<Pasted image 20231102192743.png>)

如果希望传递的参数中包含空格（例如一个名为 My Photos 的文件夹），您要么用使用单引号``'My Photos'``，双引号将其包裹起来 ``"My Photos"`` ，要么使用转义符号 `\` 进行处理（``My\ Photos``）。

![Alt text](<Pasted image 20231102192947.png>)

**环境变量** 是 shell 确定程序位置的一个基本方法，它就像编程语言的一种变量（实际上 shell 就是一种编程语言，可以用来编程，后面可以来写脚本）。它是在启动 shell 的时候就已经设置好了的，不需要用户每次手动配置

**路径变量** `$PATH` 是一类重要的环境变量：如果你要求 shell 执行某个指令，但是该指令并不是 shell 所了解的编程关键字，那么它会去咨询 _环境变量_ `$PATH`，其会列出当 shell 接到某条指令时，进行程序搜索的路径

![Alt text](<Pasted image 20231102193152.png>)

这是由冒号所分割的路径列表。电脑在`$PATH`寻找并尝试匹配你所需要的程序。

运行程序可以直接输入程序名称，让 shell 从 `$PATH` 中寻找它，或者通过程序的**绝对路径**来运行

绝对路径是完全可以确定文件位置的路径

相对路径是*相对你所在路径*的路径。利用 `pwd` 命令可以查看当前所在的路径


![Alt text](<Pasted image 20231102193940.png>)

其告诉我我正位于 `C:\Users\Azusaislit` 文件夹中（我目前使用Windows系统下的Bash shell）

而切换目录需要使用 `cd` 命令。在路径中，`.` 表示的是当前目录，而 `..` 表示上级目录

如果我们想知道所运行的程序是哪一个，我们可使用 `which` 命令

![](<Pasted image 20231102193432.png>)
即运行的 `echo` 程序位于 `/usr/bin/echo` 

在Windows上，每个分区都有一个根目录，每个分区都有一个单独的路径结构： `C:\` `D:\`，而这样的路径用**反斜杠**分割

在Linux和MacOS，所有内容都属于根命名空间内，所有绝对路径都由 `/` 开头，路径用**正斜杠**分割。

为了查看指定目录下包含哪些文件，我们使用 `ls` 命令：
![](<Pasted image 20231102194631.png>)
这告诉我们 `C:\Users\Azusaislit\Pictures` 路径下的所有文件夹（蓝色字体）与文件（白色字体）
使用 `ls -l` 命令会给我们有关这些文件夹与文件的更多信息

![](<Pasted image 20231102195307.png>)

在某些条目的开头的 "d" 表示这些条目是一个目录，因此我们可知道 `'Camera Roll'` 条目 是一个目录，而 `desktop.ini` 是一个文件。
之后的9个字母表示该文件或目录的权限：有 "r" 意思是读取权限，有 "w" 意思是写入权限，有 "x" 意思是执行权限。

如 `r-x` 意思是你拥有读取与执行权限，但没有写入权限。
而对目录来说，这些权限含义

- 读取 -> 查看目录的文件列表
- 写入 -> 在目录中**创造、重命名、删除**文件。
（如果你有文件 `/usr/bin/programA/config.yoml` 的写入权限，但没有目录 `/usr/bin/programA` 的写入权限，这意味着你可以对 该yoml本身内容进行操作，却不能重命名它、或者删除它）
- 执行 -> "搜索"权限，是否允许进入该目录。如果你要进入一个目录，你需要在 **该目录及其所有的直系父目录上** 都拥有执行权限

前三个字符是为文件所有者（这里是Azusaislit）所设置的权限
中间三个字符是为拥有该文件的组设置的权限
最后三个字符是其他人的权限列表

对于 `cd` 命令有两个特殊符号较常用：
- `cd ~` 将切换到主目录（不是根目录）
- `cd -` 将切换到你之前所在的目录


![](<Pasted image 20231102195008.png>)

如图，通过 `cd -` 我们实现了在 `~/pictures` 与  `~` 之间相互切换

`mv` 命令可以 **移动文件** ，也可以 **重命名文件**

![Alt text](<Pasted image 20231102200558.png>)

利用 `mv` 命令将当前所在路径下的一个 `broke.txt` 重命名为 `up.txt`

![Alt text](<Pasted image 20231102200822.png>)

利用 `mv` 命令将位于 `D:\ST2` 的 `hello.txt` 转移到 `D:\Shell_test` 目录

![Alt text](<Pasted image 20231102200944.png>)

同样 **重命名** 和 **移动** 操作 **可以同时进行**

还有 `cp` 命令可用于复制文件，用法类似 `mv` ，也可以用来重命名文件

![!\[\[Pasted image 20231102201110.png\]\]](<Pasted image 20231102201110.png>)

`rm` 命令可以用来删除文件，但在Linux上删除不会递归进行，因此不能用于删除目录。通常使用 `rm -r` 或者 `rmdir` 命令用于删除目录，但后者只能删除空目录。

![!\[\[Pasted image 20231102201230.png\]\]](<Pasted image 20231102201230.png>)

`mkdir` 命令用于创建目录。如果你要创建一个名为 `My Photo` 的目录，您要么用使用单引号``'My Photos'``，双引号将其包裹起来 ``"My Photos"`` ，要么使用转义符号 `\` 进行处理（``My\ Photos``）。

`man` 程序以另一个程序作为参数，并给出作为参数的程序的 manual pages。这比 --help 指令通常更为实用。（Windows的bash不可用）

`Ctrl + L` 是 `cls` (Windows cmd) 或 `clear` (Bash Shell) 的快捷键

在 shell 中，程序有两个主要的“流”：它们的输入流和输出流。 当程序尝试读取信息时，它们会从输入流中进行读取，当程序打印信息时，它们会将信息输出到输出流中。 通常，一个程序的输入输出流都是您的终端。也就是，您的键盘作为输入，显示器作为输出。 但是，我们也可以重定向这些流！

最简单的重定向是 `< file` ：表示将要运行的程序的输入重定向为 `file` 文件的内容（`file` 代替输入）
和 `> file` ：表示将程序的输出重定向到 `file` 文件中（将 `file` 用于输出结果）

![Alt text](<Pasted image 20231102201830.png>)

`cat` 命令的作用是打印文件的内容。我们可以看到 `echo` 命令的结果被写入到 `hello.txt` 中了。

![Alt text](<Pasted image 20231102202019.png>)

利用 `cat` 命令也重定向输入输出：从 `hello.txt` 读取内容，并输出在 `hate.txt` 中。最后一个 `cat` 命令中输出没有重定向，其内容默认输出在终端上。

`|` 操作符允许我们将一个程序的输出和另外一个程序的输入连接起来: `A | B` 即将 A 程序的输出作为 B程序的输入。`|` 的使用可以嵌套。
``
`tail`

`sudo su` 将终端切换到 ROOT终端

`tee`  

```
echo 1060 | sudo tee brightness
```

或者
```
sudo su
echi 1060 > brightness
```

`find` 文件

`xdg-open file` 命令可以用合适的程序打开 `file` 文件。